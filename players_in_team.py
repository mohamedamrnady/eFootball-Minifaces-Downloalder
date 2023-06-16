import requests
from bs4 import BeautifulSoup as bs

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}


def players_in_team(url):
    all_players = []

    r = requests.get(url, headers=headers)
    soup = bs(r.content, "html.parser")
    players_div = soup.find_all("div", attrs={"class": "player-card-container"})
    if len(players_div) == 5:
        for counter, players in enumerate(players_div):
            if counter == 4:
                players_url = players.find_all("a")
                for player_url in players_url:
                    original_link = player_url.get_attribute_list("href")[0].split(
                        "/player/"
                    )
                    real_player_id = str(
                        int(
                            hex(int(original_link[1].replace("/", "")))[-5:],
                            base=16,
                        )
                    )
                    final_url = f"https://www.pesmaster.com{original_link[0]}/player/{real_player_id}/"
                    try:
                        all_players.index(final_url)
                    except:
                        all_players.append(final_url)
    return all_players
