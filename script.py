import os
import requests
from bs4 import BeautifulSoup as bs
from get_miniface import miniface_downloader
from teams import league_info_scrapper, teams_urls_scrapper
from players_in_team import players_in_team

cwdir = os.path.join("MinifaceServer", "content", "miniface-server")
if not os.path.exists(cwdir):
    os.makedirs(cwdir)
os.chdir(cwdir)
print("Loading Info...")

leagues_urls = league_info_scrapper(
    "https://www.pesmaster.com/efootball-2022/", "url", 2022
)
leagues_names = league_info_scrapper(
    "https://www.pesmaster.com/efootball-2022/", "name", 2022
)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

done_players = []
print("Loaded!")

for counter, league_url in enumerate(leagues_urls):
    print(
        "Started League ("
        + str(counter + 1)
        + "/"
        + str(len(leagues_urls))
        + ") : "
        + leagues_names[counter]
    )
    teams_urls = teams_urls_scrapper(league_url)
    for team_url in teams_urls:
        players_urls = players_in_team(team_url)
        for player_url in players_urls:
            player_id = str(player_url.split("/player/")[-1].split("/")[0])
            if not player_id in done_players:
                r = requests.get(player_url, headers=headers)
                soup = bs(r.content, "html.parser")
                cards_div = soup.find_all(
                    "div", attrs={"class": "player-card-container"}
                )
                try:
                    cards_div = cards_div[len(cards_div) - 1].find_all(
                        "figure", attrs={"class": "player-card efootball-2022"}
                    )
                except IndexError as e:
                    print(f"Skipped {player_url} : {e}")
                    continue
                for i, card in enumerate(cards_div):
                    miniface_downloader(card, player_id)
                    done_players.append(player_id)
