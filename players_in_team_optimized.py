import requests
from bs4 import BeautifulSoup as bs
import sys
import time

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

REQUEST_TIMEOUT = 30  # Timeout for requests
REQUEST_DELAY = 0.05  # Small delay to be respectful


def log_error(message):
    """Always print error messages"""
    print(f"[ERROR] {message}", file=sys.stderr)


def log_debug(message):
    """Print debug messages only if in debug mode"""
    import os

    if os.getenv("DEBUG") or globals().get("DEBUG", False):
        print(f"[DEBUG] {message}")


def players_in_team(url):
    """
    Optimized version with better error handling and timeouts
    """
    all_players = []

    try:
        time.sleep(REQUEST_DELAY)  # Be respectful to the server
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()  # Raise an exception for bad status codes

        soup = bs(r.content, "html.parser")
        players_div = soup.find_all("div", attrs={"class": "player-card-container"})

        if len(players_div) == 5:
            for counter, players in enumerate(players_div):
                if counter == 4:
                    players_url = players.find_all("a")
                    for player_url in players_url:
                        try:
                            original_link = player_url.get_attribute_list("href")[
                                0
                            ].split("/player/")
                            real_player_id = str(
                                int(
                                    hex(int(original_link[-1].replace("/", "")))[-5:],
                                    base=16,
                                )
                            )
                            final_url = f"https://www.pesmaster.com{original_link[0]}/player/{real_player_id}/"
                            if final_url not in all_players:
                                all_players.append(final_url)
                        except (ValueError, IndexError) as e:
                            log_error(f"Error processing player URL in team {url}: {e}")
                            continue

    except requests.RequestException as e:
        log_error(f"Error fetching team {url}: {e}")
    except Exception as e:
        log_error(f"Unexpected error processing team {url}: {e}")

    return all_players
