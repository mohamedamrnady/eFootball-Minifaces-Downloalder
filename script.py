import os
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

done_players = []
print("Loaded!")

national_names = []
national_urls = []

for counter, league_url in enumerate(leagues_urls):
    if leagues_names[counter].find("National") == -1:
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
                if not player_url in done_players:
                    miniface_downloader(player_url)
                    done_players.append(player_url)
    else:
        national_names.append(leagues_names[counter])
        national_urls.append(league_url)

for counter, national_url in enumerate(national_urls):
    print(
        "Started Nation ("
        + str(counter + 1)
        + "/"
        + str(len(national_urls))
        + ") : "
        + national_names[counter]
    )
    teams_urls = teams_urls_scrapper(national_url)
    for team_url in teams_urls:
        players_urls = players_in_team(team_url)
        for player_url in players_urls:
            if not player_url in done_players:
                miniface_downloader(player_url)
                done_players.append(player_url)
