from update_func import *
from png_to_dds import *
from datetime import date


def get_last_thursday_date():
    today = date.weekday(date.today())
    day = int(str(date.today()).split("-")[2])
    if today < 3:
        thursday = day - today - 4
    if today > 3:
        thursday = day - today + 3
    if thursday < 10:
        thursday = str(0) + str(thursday)
    return str(date.today()).split(
        "-")[0] + "-" + str(date.today()).split("-")[1] + "-" + str(thursday)


url = 'https://www.pesmaster.com/efootball-2022/player/featured/?date=' + \
    get_last_thursday_date()

for player_url in players_in_update(url):
    miniface_downloader(player_url)
    png_to_dds()
    sort_all_images(get_last_thursday_date())
