from update_func import *
from png_to_dds import *
from datetime import date


def get_last_thursday_date():
    thursday = 3
    today = date.weekday(date.today())
    day = int(str(date.today()).split("-")[2])
    month = int(str(date.today()).split("-")[1])
    year = int(str(date.today()).split("-")[0])
    if today < 3:
        thursday = day - today - 4
    if today > 3:
        thursday = day - today + 3
    if thursday < 0:
        month -= 1
        if month == 0:
            month = 12
            year -= 1
        if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
            thursday += 31
        if month == 4 or month == 6 or month == 9 or month == 11:
            thursday += 30
        if month == 2:
            if (year / 4).denominator != 1:
                thursday += 28
            if (year / 4).denominator == 1:
                thursday += 29
    if thursday < 10:
        thursday = str(0) + str(thursday)
    if month < 10:
        month = str(0) + str(thursday)
    return f"{str(year)}-{str(month)}-{str(thursday)}"


url = 'https://www.pesmaster.com/efootball-2022/player/featured/?date=' + \
    get_last_thursday_date()

for player_url in players_in_update(url):
    miniface_downloader(player_url)
    png_to_dds()
    sort_all_images(get_last_thursday_date())
