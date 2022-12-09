import requests
from bs4 import BeautifulSoup as bs

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}


def players_in_update(url):
    all_players = []
    r = requests.get(url, headers=headers)
    soup = bs(r.content, 'html.parser')
    soup.find('a').get_attribute_list
    players_div = soup.find_all(
        'div', attrs={'class': 'player-card-container'})
    for players in players_div:
        players_url = players.find_all('a')
        for player_url in players_url:
            player_url = player_url.get_attribute_list('href')[0]
            all_players.append('https://www.pesmaster.com' + player_url)
    return all_players


def miniface_downloader(url):
    all_pictures = []
    soup = bs(requests.get(url, headers=headers).content, 'html.parser')

    cards_div = soup.find_all(
        'div', attrs={'class': 'player-card-container'})
    try:
        for pictures in cards_div[0].find_all('img'):
            if pictures['data-src'].find('Variation2022') != -1:
                picture_url = 'https://www.pesmaster.com' + \
                    pictures['data-src']
                picture_name = str(picture_url.split(
                    '/Variation2022/')[1].split('/')[0])
                if picture_name.find('b') == -1:
                    all_pictures.append(picture_url)
        if len(all_pictures) != 0:
            open(str(cards_div[0].find_all('a')[0]['href'].split('/player/')[1].split('/')[0]) + '.png', "wb").write(
                requests.get(all_pictures[len(all_pictures) - 1]).content)
    except:
        pass


miniface_downloader(
    'https://www.pesmaster.com/son-heung-min/efootball-2022/player/52781121579063/')
