from get_miniface import *
from teams import *
from players_in_team import *
from png_to_dds import *

print('Loading Info...')

leagues_urls = league_info_scrapper(
    'https://www.pesmaster.com/efootball-2022/', 'url', 2022)
leagues_names = league_info_scrapper(
    'https://www.pesmaster.com/efootball-2022/', 'name', 2022)

print('Loaded!')

for counter, league_url in enumerate(leagues_urls):
    if leagues_names[counter].find('National') == -1:
        print('Started League (' + str(counter + 1) + '/' +
              str(len(leagues_urls)) + ') : ' + leagues_names[counter])
        teams_urls = teams_urls_scrapper(league_url)
        for team_url in teams_urls:
            players_urls = players_in_team(team_url)
            for player_url in players_urls:
                miniface_downloader(player_url)
        png_to_dds()
        sort_all_images(leagues_names[counter])
