import os
import requests
from get_miniface import miniface_downloader
from teams import players_in_update

if not os.path.exists("MinifaceServer\\content\\miniface-server"):
    os.makedirs("MinifaceServer\\content\\miniface-server")
os.chdir("MinifaceServer\\content\\miniface-server")

url = requests.get("https://www.pesmaster.com/efootball-2022/player/featured/").url
for player_url in players_in_update(url):
    miniface_downloader(player_url, True)
