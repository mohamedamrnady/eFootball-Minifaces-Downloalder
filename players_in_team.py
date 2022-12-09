import requests
from bs4 import BeautifulSoup as bs

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}


def players_in_team(url):
    all_players = []
    soup = bs(requests.get(url, headers=headers).content, 'html.parser')
    soup.find('a').get_attribute_list
    players_div = soup.find_all(
        'div', attrs={'class': 'player-card-container'})
    for counter, players in enumerate(players_div):
        if counter != 4:
            players_url = players.find_all('a')
            for player_url in players_url:
                player_url = player_url.get_attribute_list('href')[0]
                all_players.append('https://www.pesmaster.com' + player_url)
    return all_players
