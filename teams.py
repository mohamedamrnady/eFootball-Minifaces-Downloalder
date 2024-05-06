import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import os

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}
pes_version = "2021"

cwd = os.getcwd()
errorhappened = False


def teams_urls_scrapper(url):
    urls = []
    r = requests.get(url, headers=headers)
    soup = bs(r.content, "html.parser")
    teams_urls_div = soup.find("div", attrs={"class": "team-block-container"}).find_all(
        "div", attrs={"class": "team-block"}
    )
    for team_url_div in teams_urls_div:
        team_url = team_url_div.find("a").get_attribute_list("href")[0]
        team_url = "https://www.pesmaster.com/" + team_url
        urls.append(team_url)
    return urls


def league_info_scrapper(url, needed, pes_version):
    league_ids = []
    league_names = []
    league_urls = []
    if pes_version <= 2021:
        url = url.replace("efootball-", "pes-")
    if pes_version >= 2022:
        url = url.replace("pes-", "efootball-")
    url_year = url.find("-20")
    url = url[:url_year] + "-" + str(pes_version) + "/"

    r = requests.get(url, headers=headers)
    soup = bs(r.content, "html.parser")

    # team_names_div = soup.find('div').find('h2', attrs={'id': 'leagues'})
    team_names_div = soup.find_all("div", attrs={"class": "team-block-container"})
    # print(team_names_div)
    for position, team_name_div in enumerate(team_names_div):
        if position == 2 or position == 1 and pes_version >= 2022:
            teams_names = team_name_div.find_all(
                "span", attrs={"class": "team-block-name"}
            )
            teams_ids = team_name_div.find_all("a")
            if needed == "name":
                for team_name in teams_names:
                    league_names.append(team_name.text)
                return league_names
            for team_id in teams_ids:
                team_id = team_id.get_attribute_list("href")[0]
                if needed == "url":
                    team_url = "https://www.pesmaster.com/" + team_id
                    league_urls.append(team_url)
                if needed == "id":
                    team_id = str(team_id).split("/league/")[-1].split("/")[0]
                    league_ids.append(team_id)
    if needed == "url":
        return league_urls
    if needed == "id":
        return league_ids


def players_in_update(url):
    all_players = []
    r = requests.get(url, headers=headers)
    soup = bs(r.content, "html.parser")
    players_div = soup.find_all("div", attrs={"class": "player-card-container"})
    for players in players_div:
        players_url = players.find_all("a")
        for player_url in players_url:
            player_url = player_url.get_attribute_list("href")[0]
            all_players.append("https://www.pesmaster.com" + player_url)
    return all_players
