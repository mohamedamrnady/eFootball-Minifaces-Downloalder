import os
import requests
from bs4 import BeautifulSoup as bs
from get_miniface import miniface_downloader

cwdir = os.path.join("MinifaceServer", "content", "miniface-server")
if not os.path.exists(cwdir):
    os.makedirs(cwdir)
os.chdir(cwdir)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

url = requests.get("https://www.pesmaster.com/efootball-2022/player/featured/").url

r = requests.get(url, headers=headers)
soup = bs(r.content, "html.parser")
cards_div = soup.find_all("div", attrs={"class": "player-card-container"})
for cards in cards_div:
    for card in cards.find_all("figure", attrs={"class": "player-card efootball-2022"}):
        miniface_downloader(card)
