import os
import requests
import threading
import sys
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as bs
from wand import image
import time

# Thread-safe storage for downloaded events
downloaded_events_lock = threading.Lock()
downloaded_events = {"names": [], "bytes": []}

# Thread-safe locks for directory and file operations
directory_creation_lock = threading.Lock()
file_save_lock = threading.Lock()

# Configuration for image downloads
MAX_IMAGE_WORKERS = 4
IMAGE_REQUEST_DELAY = 0.05  # Small delay between image requests


def log_error(message):
    """Always print error messages"""
    print(f"[ERROR] {message}", file=sys.stderr)


def log_debug(message):
    """Print debug messages only if in debug mode"""
    # We'll check for a global DEBUG flag or environment variable
    import os

    if os.getenv("DEBUG") or globals().get("DEBUG", False):
        print(f"[DEBUG] {message}")


def save_miniface_image(player_id, image_dict, with_background=True, base_dir="."):
    """
    Save miniface image to disk with proper thread safety.

    Args:
        player_id: Player ID for directory structure
        image_dict: Dictionary containing image data (bytes, background_bytes, team, id)
        with_background: If True, composite background with foreground; if False, save foreground only
        base_dir: Base directory for saving (relative or absolute path)

    Returns:
        bool: True if save successful, False otherwise
    """
    if not image_dict["bytes"]:
        log_debug(f"No foreground image for player {player_id}, skipping save")
        return False

    # For background version, we need both images
    if with_background and not image_dict["background_bytes"]:
        log_debug(
            f"No background image for player {player_id}, skipping background save"
        )
        return False

    try:
        # Thread-safe directory creation for player
        player_dir = os.path.join(base_dir, player_id)
        with directory_creation_lock:
            if not os.path.exists(player_dir):
                os.makedirs(player_dir)

        # Thread-safe directory creation for team
        team_dir = os.path.join(player_dir, image_dict["team"])
        with directory_creation_lock:
            if not os.path.exists(team_dir):
                os.makedirs(team_dir)

        fn = os.path.join(team_dir, image_dict["id"] + ".dds")

        # Thread-safe file save with atomic check-then-save
        with file_save_lock:
            if os.path.exists(fn):
                log_debug(f"File already exists: {fn}")
                return True

            # Image processing
            if with_background:
                # Composite version (background + foreground)
                back_img = image.Image(blob=image_dict["background_bytes"])
                fore_img = image.Image(blob=image_dict["bytes"])
                back_img.trim(percent_background=0.5)
                back_img.resize(fore_img.width, fore_img.height)
                back_img.composite(fore_img)
                back_img.compression = "dxt5"
                back_img.save(filename=fn)
            else:
                # No-background version (foreground only)
                fore_img = image.Image(blob=image_dict["bytes"])
                fore_img.compression = "dxt5"
                fore_img.save(filename=fn)

            log_debug(
                f"Saved {'background' if with_background else 'no-background'} image: {fn}"
            )
            return True

    except Exception as e:
        log_error(
            f"Error saving {'background' if with_background else 'no-background'} image for player {player_id}: {e}"
        )
        return False


def miniface_downloader(
    card, player_id=None, output_dir_standard=None, output_dir_background=None
):
    """
    Thread-safe version of miniface downloader with concurrent image processing.
    Saves to both standard (no-background) and background versions.

    Args:
        card: BeautifulSoup card element to process
        player_id: Optional player ID (will be extracted if not provided)
        output_dir_standard: Directory for no-background version (default: current directory)
        output_dir_background: Directory for background version (default: None, skips background save)
    """
    if output_dir_standard is None:
        output_dir_standard = "."

    if output_dir_standard is None:
        output_dir_standard = "."

    image_dict = {
        "team": "",
        "default": True,
        "bytes": False,
        "id": "",
        "background_bytes": False,
    }

    pictures_div = card.find_all("img")
    image_download_tasks = []

    for pictures in pictures_div:
        if "teamlogos" in pictures["data-src"]:
            image_dict["team"] = str(
                int(
                    pictures["data-src"]
                    .split("/teamlogos/")[1]
                    .split("/")[0]
                    .replace(".png", "")
                    .replace("e_", "")
                    .replace("_w", "")
                )
            )
        elif "graphics/players" in pictures["data-src"]:
            picture_url = "https://www.pesmaster.com" + pictures["data-src"]
            if "/Variation2022/" in pictures["data-src"]:
                picture_name = str(
                    picture_url.split("/Variation2022/")[-1].split("/")[0]
                )
                image_dict["default"] = False
            else:
                picture_name = str(
                    picture_url.split("graphics/players/")[-1].split("/")[0]
                )
                image_dict["default"] = True

            if not "b" in picture_name and not "dummy" in picture_name:
                if not image_dict["default"]:
                    image_download_tasks.append(("main", picture_url, picture_name))
                image_dict["id"] = picture_name.replace("_.png", "")
            elif "_b02" in picture_name:
                image_download_tasks.append(("background", picture_url, picture_name))

    # Download images concurrently
    if image_download_tasks:
        with ThreadPoolExecutor(max_workers=MAX_IMAGE_WORKERS) as executor:
            futures = {}
            for img_type, url, name in image_download_tasks:
                if img_type == "main":
                    future = executor.submit(download_image, url)
                    futures[future] = ("main", name)
                elif img_type == "background":
                    future = executor.submit(get_card_event, name, url)
                    futures[future] = ("background", name)

            # Collect results
            for future in futures:
                img_type, name = futures[future]
                try:
                    result = future.result()
                    if img_type == "main":
                        image_dict["bytes"] = result
                    elif img_type == "background":
                        image_dict["background_bytes"] = result
                except Exception as e:
                    log_error(f"Error downloading {img_type} image {name}: {e}")

    # Determine player_id if not provided
    if not player_id:
        try:
            player_id = str(
                int(
                    hex(int(image_dict["id"].split("/player/")[-1].split("/")[0]))[-6:],
                    base=16,
                )
            )
        except (ValueError, IndexError):
            log_error(f"Could not determine player_id from {image_dict['id']}")
            return

    # Save both versions: no-background and with-background
    if image_dict["bytes"] and image_dict["background_bytes"]:
        # Save to standard directory (no background)
        save_miniface_image(
            player_id,
            image_dict,
            with_background=False,
            base_dir=output_dir_standard,
        )

        # Save to background directory if specified
        if output_dir_background:
            save_miniface_image(
                player_id,
                image_dict,
                with_background=True,
                base_dir=output_dir_background,
            )


def download_image(url: str, fallback_attempted=False):
    """
    Download image with retry logic and proper error handling
    """
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            # Add small delay to be respectful to the server
            time.sleep(IMAGE_REQUEST_DELAY)

            r = requests.get(url, timeout=30)
            if r.status_code == 200 and not r.content.startswith(b"<!DOCTYPE html>"):
                return r.content
            else:
                # Only try fallbacks once to prevent infinite recursion
                if not fallback_attempted:
                    if "pesmaster" in url and "Variation2022" in url:
                        fallback_url = url.replace(
                            "https://www.pesmaster.com/efootball-2022/graphics/players/Variation2022/",
                            "https://efootballhub.net/images/efootball23/players/",
                        )
                        return download_image(fallback_url, fallback_attempted=True)
                    elif "efootball23" in url:
                        fallback_url = url.replace("efootball23", "efootball24")
                        return download_image(fallback_url, fallback_attempted=True)

                # No valid fallback or fallback already attempted
                log_debug(f"Image not found (HTTP {r.status_code}): {url}")
                return False

        except requests.RequestException as e:
            if attempt < max_retries - 1:
                log_debug(f"Retry {attempt + 1}/{max_retries} for {url}: {e}")
                time.sleep(retry_delay * (attempt + 1))
            else:
                log_error(f"Failed to download {url} after {max_retries} attempts: {e}")
                return False
        except Exception as e:
            log_error(f"Unexpected error downloading {url}: {e}")
            return False

    return False


def get_card_event(event_name, event_url):
    """
    Thread-safe event downloading with caching
    """
    # Thread-safe check for cached event
    with downloaded_events_lock:
        if event_name in downloaded_events["names"]:
            index = downloaded_events["names"].index(event_name)
            return downloaded_events["bytes"][index]

    # Download the event
    b = download_image(event_url)

    # Thread-safe caching
    with downloaded_events_lock:
        # Double-check in case another thread added it while we were downloading
        if event_name not in downloaded_events["names"]:
            downloaded_events["names"].append(event_name)
            downloaded_events["bytes"].append(b)

    return b
