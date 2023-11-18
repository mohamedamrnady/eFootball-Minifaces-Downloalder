from get_miniface import *
from teams import *
from png_to_dds import *
import requests

url = requests.get("https://www.pesmaster.com/efootball-2022/player/featured/").url
for player_url in players_in_update(url):
    miniface_downloader(player_url)
    png_to_dds()
    sort_all_images(url.split("date=")[1])
