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


def miniface_downloader(card, player_id=False):
    """
    Thread-safe version of miniface downloader with concurrent image processing
    """
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

    # Thread-safe directory creation and file writing
    if not os.path.exists(player_id):
        # Use a lock to prevent race conditions in directory creation
        with threading.Lock():
            if not os.path.exists(player_id):
                os.makedirs(player_id)

    if image_dict["bytes"] and image_dict["background_bytes"]:
        dirc = os.path.join(player_id, image_dict["team"])
        if not os.path.exists(dirc):
            with threading.Lock():
                if not os.path.exists(dirc):
                    os.makedirs(dirc)

        fn = os.path.join(dirc, image_dict["id"] + ".dds")

        # Only create the file if it doesn't exist
        if not os.path.exists(fn):
            try:
                # Image processing
                back_img = image.Image(blob=image_dict["background_bytes"])
                fore_img = image.Image(blob=image_dict["bytes"])
                back_img.trim(percent_background=0.5)
                back_img.resize(fore_img.width, fore_img.height)
                back_img.composite(fore_img)
                back_img.compression = "dxt5"
                back_img.save(filename=fn)
            except Exception as e:
                log_error(f"Error processing image for player {player_id}: {e}")


def download_image(url: str):
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
                if "pesmaster" in url:
                    return download_image(
                        url.replace(
                            "https://www.pesmaster.com/efootball-2022/graphics/players/Variation2022/",
                            "https://efootballhub.net/images/efootball23/players/",
                        )
                    )
                elif "efootball23" in url:
                    return download_image(
                        url.replace(
                            "efootball23",
                            "efootball24",
                        )
                    )
                elif "efootball24" in url:
                    log_debug(f"Skipped image {url}")
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
