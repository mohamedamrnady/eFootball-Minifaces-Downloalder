import os
import requests
import threading
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup as bs
from get_miniface import miniface_downloader

# Import configuration with fallbacks
try:
    from config import (
        MAX_WORKERS_PLAYERS,
        MAX_WORKERS_IMAGES,
        REQUEST_DELAY,
        REQUEST_TIMEOUT,
    )
except ImportError:
    # Fallback configuration if config.py doesn't exist
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
        debug_print(
            f"Loaded {len(skipped_players)} skipped players from {SKIPPED_FILE}"
        )
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
        description="Optimized eFootball Featured Players Downloader with multithreading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get_update_only.py                    # Run with default settings
  python get_update_only.py --debug           # Run with debug logging
  python get_update_only.py -d --quiet        # Debug mode with minimal output
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
        "--workers",
        type=int,
        help="Override number of concurrent players (default from config.py)",
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
    global DEBUG, MAX_WORKERS_PLAYERS, MAX_WORKERS_IMAGES, REQUEST_DELAY, REQUEST_TIMEOUT

    # Parse command line arguments
    args = parse_arguments()
    DEBUG = args.debug
    QUIET = args.quiet

    # Import configuration with fallbacks
    try:
        from config import (
            MAX_WORKERS_PLAYERS as DEFAULT_PLAYERS,
            MAX_WORKERS_IMAGES as DEFAULT_IMAGES,
            REQUEST_DELAY as DEFAULT_DELAY,
            REQUEST_TIMEOUT as DEFAULT_TIMEOUT,
        )

        debug_print("Configuration loaded from config.py")
    except ImportError:
        DEFAULT_PLAYERS = 8
        DEFAULT_IMAGES = 6
        DEFAULT_DELAY = 0.1
        DEFAULT_TIMEOUT = 30
        log_error("config.py not found, using default configuration")

    # Apply command line overrides
    MAX_WORKERS_PLAYERS = args.workers if args.workers else DEFAULT_PLAYERS
    MAX_WORKERS_IMAGES = DEFAULT_IMAGES
    REQUEST_DELAY = args.delay if args.delay else DEFAULT_DELAY
    REQUEST_TIMEOUT = DEFAULT_TIMEOUT

    if not QUIET:
        print("Loading Featured Players...")
    debug_print(f"Configuration: Players={MAX_WORKERS_PLAYERS}, Delay={REQUEST_DELAY}s")

    # Load persistent skip list so we can avoid HTTP requests early
    load_skipped_players()

    return args


def extract_player_id_from_card(card):
    """Extract player ID from a card element"""
    try:
        # Look for player URL in the card
        player_link = card.find("a", href=True)
        if player_link and "/player/" in player_link["href"]:
            return str(
                int(
                    hex(int(player_link["href"].split("/player/")[-1].split("/")[0]))[
                        -6:
                    ],
                    base=16,
                )
            )
    except Exception as e:
        debug_print(f"Could not extract player ID from card: {e}")
    return None


def process_featured_card(card):
    """Process a single featured player card"""
    try:
        player_id = extract_player_id_from_card(card)
        if not player_id:
            debug_print("Could not extract player ID from card")
            return "✗ Could not extract player ID"

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

        debug_print(f"Processing featured player {player_id}")

        # Add small delay to be respectful to the server
        time.sleep(REQUEST_DELAY)

        # Process the card directly
        miniface_downloader(card, player_id)

        # Success: do not add to skip list (only skipping 'not found' players)
        log_success(f"Processed featured player {player_id}")
        return f"✓ Processed featured player {player_id}"

    except Exception as e:
        log_error(f"Error processing featured card: {e}")
        return f"✗ Error processing featured card: {e}"


def main():
    """Main function to download featured players"""
    args = initialize_script()

    if not args.quiet:
        print(f"Starting featured players download with {MAX_WORKERS_PLAYERS} workers")

    debug_print("Debug mode enabled - verbose logging active")
    debug_print(
        f"Configuration: Players={MAX_WORKERS_PLAYERS}, Images={MAX_WORKERS_IMAGES}"
    )
    debug_print(f"Request delay: {REQUEST_DELAY}s, Timeout: {REQUEST_TIMEOUT}s")

    overall_start_time = time.time()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }

    try:
        if not args.quiet:
            print("Fetching featured players page...")

        # Get the featured players page
        url = requests.get(
            "https://www.pesmaster.com/efootball-2022/player/featured/",
            timeout=REQUEST_TIMEOUT,
        ).url
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        soup = bs(r.content, "html.parser")
        cards_div = soup.find_all("div", attrs={"class": "player-card-container"})

        if not cards_div:
            log_error("No player cards found on featured players page")
            return

        # Extract all featured player cards
        all_cards = []
        for cards_container in cards_div:
            featured_cards = cards_container.find_all(
                "figure", attrs={"class": "player-card efootball-2022"}
            )
            all_cards.extend(featured_cards)

        if not all_cards:
            log_error("No efootball-2022 featured cards found")
            return

        debug_print(f"Found {len(all_cards)} featured player cards")

        # Filter out cards for players in the persistent skip list
        filtered_cards = []
        with skipped_players_lock:
            for card in all_cards:
                player_id = extract_player_id_from_card(card)
                if player_id and player_id not in skipped_players:
                    filtered_cards.append(card)

        skipped_count = len(all_cards) - len(filtered_cards)
        if skipped_count > 0:
            debug_print(f"Skipping {skipped_count} players from skip list")

        if not args.quiet:
            print(f"Processing {len(filtered_cards)} featured players...")

        # Process featured players concurrently
        successful_players = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_PLAYERS) as executor:
            futures = {
                executor.submit(process_featured_card, card): card
                for card in filtered_cards
            }

            for future in as_completed(futures):
                result = future.result()
                if result.startswith("✓"):
                    successful_players += 1
                    debug_print(f"    {result}")
                elif result.startswith("✗"):
                    debug_print(f"    {result}")

        overall_elapsed_time = time.time() - overall_start_time

        with done_players_lock:
            total_players = len(done_players)

        # Final summary (always shown)
        print(
            f"\n🎉 Featured players download complete! Processed {total_players} unique players in {overall_elapsed_time:.2f}s"
        )
        print(f"Success rate: {successful_players}/{len(filtered_cards)}")
        print(
            f"Average time per player: {overall_elapsed_time/max(total_players, 1):.2f}s"
        )

        if DEBUG:
            print(f"\n[DEBUG] Final Statistics:")
            print(f"[DEBUG] - Total execution time: {overall_elapsed_time:.2f}s")
            print(
                f"[DEBUG] - Players per second: {total_players/max(overall_elapsed_time, 1):.2f}"
            )
            print(f"[DEBUG] - Thread configuration used: Players={MAX_WORKERS_PLAYERS}")
            print(f"[DEBUG] - Request delay used: {REQUEST_DELAY}s")

    except requests.RequestException as e:
        log_error(f"Network error fetching featured players: {e}")
    except Exception as e:
        log_error(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Initialize and run
    main()
