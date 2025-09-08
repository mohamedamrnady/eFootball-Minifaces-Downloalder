import os
import requests
import threading
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from bs4 import BeautifulSoup as bs
from get_miniface import miniface_downloader
from teams import league_info_scrapper, teams_urls_scrapper
from players_in_team import players_in_team
import time

# Import configuration with fallbacks
try:
    from config import (
        MAX_WORKERS_TEAMS,
        MAX_WORKERS_PLAYERS,
        MAX_WORKERS_IMAGES,
        REQUEST_DELAY,
        REQUEST_TIMEOUT,
    )
except ImportError:
    # Fallback configuration if config.py doesn't exist
    MAX_WORKERS_TEAMS = 4
    MAX_WORKERS_PLAYERS = 8
    MAX_WORKERS_IMAGES = 6
    REQUEST_DELAY = 0.1
    REQUEST_TIMEOUT = 30

# Thread-safe set for tracking processed players
done_players_lock = threading.Lock()
done_players = set()

# Skipped players list (persisted between runs)
skipped_players_lock = threading.Lock()
skipped_players = set()
SKIPPED_FILE = "skipped_players.txt"

# Global debug flag
DEBUG = False


def load_skipped_players():
    """Load or create the persistent skip list file"""
    global skipped_players
    if not os.path.exists(SKIPPED_FILE):
        try:
            with open(SKIPPED_FILE, "a") as _:
                pass
        except Exception as e:
            log_error(f"Failed to create {SKIPPED_FILE}: {e}")
            return
        skipped_players = set()
        return
    try:
        with open(SKIPPED_FILE, "r") as f:
            skipped_players = set(line.strip() for line in f if line.strip())
        debug_print(f"Loaded {len(skipped_players)} skipped players from {SKIPPED_FILE}")
    except Exception as e:
        log_error(f"Failed to load {SKIPPED_FILE}: {e}")
        skipped_players = set()


def append_skipped_player(player_id: str):
    """Append a player_id to the persistent skip list in a thread-safe way"""
    try:
        with skipped_players_lock:
            if player_id not in skipped_players:
                with open(SKIPPED_FILE, "a") as f:
                    f.write(f"{player_id}\n")
                skipped_players.add(player_id)
                debug_print(f"Added {player_id} to skip list")
    except Exception as e:
        log_error(f"Failed to append {player_id} to {SKIPPED_FILE}: {e}")


def debug_print(message):
    """Print debug messages only if debug mode is enabled"""
    if DEBUG:
        print(f"[DEBUG] {message}")


def log_info(message):
    """Print info messages only if debug mode is enabled"""
    if DEBUG:
        print(f"[INFO] {message}")


def log_error(message):
    """Always print error messages"""
    print(f"[ERROR] {message}", file=sys.stderr)


def log_success(message):
    """Print success messages only if debug mode is enabled"""
    if DEBUG:
        print(f"[SUCCESS] {message}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Optimized eFootball Minifaces Downloader with multithreading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script.py                    # Run with default settings
  python script.py --debug           # Run with debug logging
  python script.py -d --quiet        # Debug mode with minimal output
        """,
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug logging (shows detailed progress and timing info)",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode - only show errors and final summary",
    )

    parser.add_argument(
        "--workers-teams",
        type=int,
        help="Override number of concurrent teams (default from config.py)",
    )

    parser.add_argument(
        "--workers-players",
        type=int,
        help="Override number of concurrent players per team (default from config.py)",
    )

    parser.add_argument(
        "--delay",
        type=float,
        help="Override request delay in seconds (default from config.py)",
    )

    return parser.parse_args()


cwdir = os.path.join("MinifaceServer", "content", "miniface-server")
if not os.path.exists(cwdir):
    os.makedirs(cwdir)
os.chdir(cwdir)


def initialize_script():
    """Initialize the script with configuration and arguments"""
    global DEBUG, MAX_WORKERS_TEAMS, MAX_WORKERS_PLAYERS, MAX_WORKERS_IMAGES, REQUEST_DELAY, REQUEST_TIMEOUT

    # Parse command line arguments
    args = parse_arguments()
    DEBUG = args.debug
    QUIET = args.quiet

    # Import configuration with fallbacks
    try:
        from config import (
            MAX_WORKERS_TEAMS as DEFAULT_TEAMS,
            MAX_WORKERS_PLAYERS as DEFAULT_PLAYERS,
            MAX_WORKERS_IMAGES as DEFAULT_IMAGES,
            REQUEST_DELAY as DEFAULT_DELAY,
            REQUEST_TIMEOUT as DEFAULT_TIMEOUT,
        )

        debug_print("Configuration loaded from config.py")
    except ImportError:
        DEFAULT_TEAMS = 4
        DEFAULT_PLAYERS = 8
        DEFAULT_IMAGES = 6
        DEFAULT_DELAY = 0.1
        DEFAULT_TIMEOUT = 30
        log_error("config.py not found, using default configuration")

    # Apply command line overrides
    MAX_WORKERS_TEAMS = args.workers_teams if args.workers_teams else DEFAULT_TEAMS
    MAX_WORKERS_PLAYERS = (
        args.workers_players if args.workers_players else DEFAULT_PLAYERS
    )
    MAX_WORKERS_IMAGES = DEFAULT_IMAGES
    REQUEST_DELAY = args.delay if args.delay else DEFAULT_DELAY
    REQUEST_TIMEOUT = DEFAULT_TIMEOUT

    if not QUIET:
        print("Loading Info...")
    debug_print(
        f"Configuration: Teams={MAX_WORKERS_TEAMS}, Players={MAX_WORKERS_PLAYERS}, Delay={REQUEST_DELAY}s"
    )

    # Load persistent skip list so we can avoid HTTP requests early
    load_skipped_players()

    return args


# Initialize and get configuration
args = initialize_script()

leagues_urls = league_info_scrapper(
    "https://www.pesmaster.com/efootball-2022/", "url", 2022
)
leagues_names = league_info_scrapper(
    "https://www.pesmaster.com/efootball-2022/", "name", 2022
)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

if not args.quiet:
    print("Loaded!")
debug_print(f"Found {len(leagues_urls)} leagues to process")


def process_player(player_url, team_name, league_name):
    """Process a single player - download and extract miniface"""
    try:
        player_id = str(player_url.split("/player/")[-1].split("/")[0])

        # Early skip if player is in persistent skip list
        with skipped_players_lock:
            if player_id in skipped_players:
                debug_print(f"Skipped {player_id} (in skip list)")
                return f"Skipped {player_id} (in skip list)"

        # Thread-safe check if player already processed
        with done_players_lock:
            if player_id in done_players:
                debug_print(f"Skipped {player_id} (already processed)")
                return f"Skipped {player_id} (already processed)"
            done_players.add(player_id)

        debug_print(f"Processing player {player_id} from {team_name}")

        # Add small delay to be respectful to the server
        time.sleep(REQUEST_DELAY)

        r = requests.get(player_url, headers=headers, timeout=REQUEST_TIMEOUT)
        soup = bs(r.content, "html.parser")
        cards_div = soup.find_all("div", attrs={"class": "player-card-container"})

        if not cards_div:
            debug_print(f"No cards found for player {player_id}")
            append_skipped_player(player_id)
            return f"No cards found for player {player_id}"

        cards_div = cards_div[len(cards_div) - 1].find_all(
            "figure", attrs={"class": "player-card efootball-2022"}
        )

        if not cards_div:
            debug_print(f"No efootball-2022 cards found for player {player_id}")
            append_skipped_player(player_id)
            return f"No efootball-2022 cards found for player {player_id}"

        for card in cards_div:
            miniface_downloader(card, player_id)

        # Persist success to skip list to avoid future page fetches
        append_skipped_player(player_id)

        log_success(f"Processed player {player_id} from {team_name}")
        return f"✓ Processed player {player_id} from {team_name}"

    except IndexError as e:
        log_error(f"IndexError for player {player_url}: {e}")
        return f"✗ IndexError for player {player_url}: {e}"
    except requests.RequestException as e:
        log_error(f"Request error for player {player_url}: {e}")
        return f"✗ Request error for player {player_url}: {e}"
    except Exception as e:
        log_error(f"Error processing player {player_url}: {e}")
        return f"✗ Error processing player {player_url}: {e}"


def process_team(team_url, team_counter, total_teams, league_name):
    """Process a single team - get all players and process them concurrently"""
    try:
        log_info(f"Processing team {team_counter}/{total_teams} in {league_name}")

        # Add small delay to be respectful to the server
        time.sleep(REQUEST_DELAY)

        players_urls = players_in_team(team_url)

        if not players_urls:
            debug_print(f"No players found for team {team_url}")
            return f"  No players found for team {team_url}"

        debug_print(f"Found {len(players_urls)} players in team {team_counter}")

        # Filter out players in the persistent skip list before scheduling requests
        with skipped_players_lock:
            filtered_players = [
                url for url in players_urls
                if str(url.split("/player/")[-1].split("/")[0]) not in skipped_players
            ]
        skipped_count = len(players_urls) - len(filtered_players)
        if skipped_count > 0:
            debug_print(f"Skipping {skipped_count} players from skip list in team {team_counter}")

        # Process players in this team concurrently
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_PLAYERS) as executor:
            player_futures = {
                executor.submit(
                    process_player, player_url, f"team_{team_counter}", league_name
                ): player_url
                for player_url in filtered_players
            }

            results = []
            successful_players = 0
            for future in as_completed(player_futures):
                result = future.result()
                results.append(result)
                if result.startswith("✓"):
                    successful_players += 1
                    debug_print(f"    {result}")
                elif result.startswith("✗"):
                    debug_print(f"    {result}")

        log_info(
            f"Completed team {team_counter}/{total_teams} in {league_name} ({successful_players}/{len(filtered_players)} players successful)"
        )
        return f"  ✓ Completed team {team_counter}/{total_teams} in {league_name} ({successful_players}/{len(filtered_players)} players)"

    except Exception as e:
        log_error(f"Error processing team {team_url}: {e}")
        return f"  ✗ Error processing team {team_url}: {e}"


def process_league(league_counter, league_url, league_name, total_leagues):
    """Process a single league - get all teams and process them concurrently"""
    try:
        if not args.quiet:
            print(
                f"\nStarted League ({league_counter + 1}/{total_leagues}): {league_name}"
            )
        debug_print(f"Processing league: {league_name} at {league_url}")
        start_time = time.time()

        teams_urls = teams_urls_scrapper(league_url)

        if not teams_urls:
            log_error(f"No teams found for league {league_name}")
            return f"No teams found for league {league_name}"

        debug_print(f"Found {len(teams_urls)} teams in {league_name}")

        # Process teams in this league concurrently
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_TEAMS) as executor:
            team_futures = {
                executor.submit(
                    process_team,
                    team_url,
                    team_counter + 1,
                    len(teams_urls),
                    league_name,
                ): team_url
                for team_counter, team_url in enumerate(teams_urls)
            }

            completed_teams = 0
            successful_teams = 0
            for future in as_completed(team_futures):
                result = future.result()
                completed_teams += 1
                if result.startswith("  ✓"):
                    successful_teams += 1
                    debug_print(result)
                elif result.startswith("  ✗"):
                    debug_print(result)

        elapsed_time = time.time() - start_time
        success_message = f"✓ Completed League {league_name} in {elapsed_time:.2f}s ({successful_teams}/{len(teams_urls)} teams successful)"
        if not args.quiet:
            print(success_message)
        debug_print(success_message)
        return success_message

    except Exception as e:
        error_message = f"✗ Error processing league {league_name}: {e}"
        log_error(error_message)
        return error_message


def main():
    """Main function to orchestrate the entire download process"""
    if not args.quiet:
        print(
            f"Starting optimized download with {MAX_WORKERS_TEAMS} team workers, {MAX_WORKERS_PLAYERS} player workers"
        )
        print(f"Total leagues to process: {len(leagues_urls)}")

    debug_print(f"Debug mode enabled - verbose logging active")
    debug_print(
        f"Configuration: Teams={MAX_WORKERS_TEAMS}, Players={MAX_WORKERS_PLAYERS}, Images={MAX_WORKERS_IMAGES}"
    )
    debug_print(f"Request delay: {REQUEST_DELAY}s, Timeout: {REQUEST_TIMEOUT}s")

    overall_start_time = time.time()

    # Process leagues sequentially to avoid overwhelming the server
    successful_leagues = 0
    for counter, league_url in enumerate(leagues_urls):
        result = process_league(
            counter, league_url, leagues_names[counter], len(leagues_urls)
        )
        if result.startswith("✓"):
            successful_leagues += 1
        elif not args.quiet:
            print(result)

    overall_elapsed_time = time.time() - overall_start_time

    with done_players_lock:
        total_players = len(done_players)

    # Final summary (always shown)
    print(
        f"\n🎉 All done! Processed {total_players} unique players in {overall_elapsed_time:.2f}s"
    )
    print(f"Leagues processed: {successful_leagues}/{len(leagues_urls)}")
    print(f"Average time per player: {overall_elapsed_time/max(total_players, 1):.2f}s")

    if DEBUG:
        print(f"\n[DEBUG] Final Statistics:")
        print(f"[DEBUG] - Total execution time: {overall_elapsed_time:.2f}s")
        print(
            f"[DEBUG] - Players per second: {total_players/max(overall_elapsed_time, 1):.2f}"
        )
        print(
            f"[DEBUG] - Thread configuration used: Teams={MAX_WORKERS_TEAMS}, Players={MAX_WORKERS_PLAYERS}"
        )
        print(f"[DEBUG] - Request delay used: {REQUEST_DELAY}s")


if __name__ == "__main__":
    main()
