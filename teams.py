import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import os
import sys
import time

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

REQUEST_TIMEOUT = 30  # Timeout for requests
REQUEST_DELAY = 0.1  # Delay between requests


def log_error(message):
    """Always print error messages"""
    print(f"[ERROR] {message}", file=sys.stderr)


def log_debug(message):
    """Print debug messages only if in debug mode"""
    import os

    if os.getenv("DEBUG") or globals().get("DEBUG", False):
        print(f"[DEBUG] {message}")


def teams_urls_scrapper(url):
    """
    Optimized version with better error handling and timeouts
    """
    urls = []
    try:
        time.sleep(REQUEST_DELAY)  # Be respectful to the server
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()

        soup = bs(r.content, "html.parser")
        team_container = soup.find("div", attrs={"class": "team-block-container"})

        if team_container:
            teams_urls_div = team_container.find_all(
                "div", attrs={"class": "team-block"}
            )
            for team_url_div in teams_urls_div:
                team_link = team_url_div.find("a")
                if team_link:
                    team_url = team_link.get_attribute_list("href")[0]
                    team_url = "https://www.pesmaster.com/" + team_url
                    urls.append(team_url)

    except requests.RequestException as e:
        log_error(f"Error fetching teams from {url}: {e}")
    except Exception as e:
        log_error(f"Unexpected error processing teams from {url}: {e}")

    return urls


def league_info_scrapper(url, needed, pes_version):
    """
    Optimized version with better error handling and timeouts
    """
    league_ids = []
    league_names = []
    league_urls = []

    try:
        if pes_version <= 2021:
            url = url.replace("efootball-", "pes-")
        if pes_version >= 2022:
            url = url.replace("pes-", "efootball-")

        url_year = url.find("-20")
        url = url[:url_year] + "-" + str(pes_version) + "/"

        time.sleep(REQUEST_DELAY)  # Be respectful to the server
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()

        soup = bs(r.content, "html.parser")
        team_names_div = soup.find_all("div", attrs={"class": "team-block-container"})

        for position, team_name_div in enumerate(team_names_div):
            if position == 2 or (position == 1 and pes_version >= 2022):
                teams_names = team_name_div.find_all(
                    "span", attrs={"class": "team-block-name"}
                )
                teams_ids = team_name_div.find_all("a")

                if needed == "name":
                    for team_name in teams_names:
                        league_names.append(team_name.text)
                    return league_names

                for team_id in teams_ids:
                    team_id_href = team_id.get_attribute_list("href")[0]
                    if needed == "url":
                        team_url = "https://www.pesmaster.com/" + team_id_href
                        league_urls.append(team_url)
                    if needed == "id":
                        team_id = str(team_id_href).split("/league/")[-1].split("/")[0]
                        league_ids.append(team_id)

    except requests.RequestException as e:
        log_error(f"Error fetching league info from {url}: {e}")
        return []
    except Exception as e:
        log_error(f"Unexpected error processing league info from {url}: {e}")
        return []

    if needed == "url":
        return league_urls
    if needed == "id":
        return league_ids
    if needed == "name":
        return league_names

    return []
