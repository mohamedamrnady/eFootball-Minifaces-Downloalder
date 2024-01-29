import enum
import requests
from bs4 import BeautifulSoup as bs
from wand import image
import os

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}


def remove_indexes(l, indexes):
    return [j for i, j in enumerate(l) if i not in indexes]


def miniface_downloader(url: str, isUpdate=False):
    all_pictures = []
    player_ids = []
    cards_team = []
    images_downloaded = []
    written_teams = []
    default_cards_indexes = []
    r = requests.get(url, headers=headers)
    soup = bs(r.content, "html.parser")
    image_name = str(url.split("/player/")[1].split("/")[0])

    cards_div = soup.find_all("div", attrs={"class": "player-card-container"})

    try:
        cards_div = cards_div[len(cards_div) - 1].find_all(
            "figure", attrs={"class": "player-card efootball-2022"}
        )
        if isUpdate:
            cards_div.insert(
                0,
                soup.find_all("figure", attrs={"class": "player-card efootball-2022"})[
                    0
                ],
            )
        for i, cards in enumerate(cards_div):
            pictures_div = cards.find_all("img")
            for pictures in pictures_div:
                if pictures["data-src"].find("teamlogos") != -1:
                    cards_team.append(
                        str(
                            int(
                                pictures["data-src"]
                                .split("/teamlogos/")[1]
                                .split("/")[0]
                                .replace(".png", "")
                                .replace("e_", "")
                            )
                        )
                    )
                elif "graphics/players" in pictures["data-src"]:
                    picture_url = "https://www.pesmaster.com" + pictures["data-src"]
                    if "/Variation2022/" in pictures["data-src"]:
                        picture_name = str(
                            picture_url.split("/Variation2022/")[1].split("/")[0]
                        )
                    else:
                        picture_name = str(
                            picture_url.split("graphics/players/")[1].split("/")[0]
                        )
                        if not i in default_cards_indexes:
                            default_cards_indexes.append(i)
                    if (
                        picture_name.find("b") == -1
                        and picture_name.find("dummy") == -1
                    ):
                        all_pictures.append(picture_url)
                        player_ids.append(picture_name.replace("_.png", ""))
        if isUpdate:
            images_downloaded.append(
                {
                    "bytes": download_image(all_pictures[0]),
                    "team": cards_team[0],
                    "id": player_ids[0],
                }
            )
        else:
            player_ids = remove_indexes(player_ids, default_cards_indexes)
            all_pictures = remove_indexes(all_pictures, default_cards_indexes)
            cards_team = remove_indexes(cards_team, default_cards_indexes)

            for i, pic in enumerate(all_pictures):
                try:
                    t = {}
                    t["bytes"] = download_image(pic)
                    t["id"] = player_ids[i]
                    try:
                        t["team"] = cards_team[i]
                    except IndexError:
                        t["team"] = cards_team[-1]
                    images_downloaded.append(t)
                except ValueError as e:
                    print(f"Skipped {str(pic)}: {e}")
        if len(all_pictures) != 0:
            if isUpdate:
                image_name = str(
                    int(
                        hex(player_ids[0])[-6:],
                        base=16,
                    )
                )
            if not os.path.exists(image_name):
                os.makedirs(image_name)
            teams_dir = os.path.join(image_name, "map_teams.csv")
            with open(teams_dir, "a") as f:
                for image_downloaded in images_downloaded:
                    dir = os.path.join(image_name, image_downloaded["team"])
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    ids_dir = os.path.join(
                        image_name, image_downloaded["team"], "map_ids.csv"
                    )
                    with open(ids_dir, "a") as ff:
                        ff.write(f"{image_downloaded['id']}\n")
                    try:
                        written_teams.index(image_downloaded["team"])
                    except ValueError as e:
                        written_teams.append(image_downloaded["team"])
                        f.write(f"{str(image_downloaded['team'])}\n")
                    with image.Image(blob=image_downloaded["bytes"]) as img:
                        img.compression = "dxt3"
                        fn = os.path.join(
                            image_name,
                            image_downloaded["team"],
                            image_downloaded["id"] + ".dds",
                        )
                        img.save(filename=fn)
    except Exception as e:
        print(f"Skipped {url}: {e}")


def download_image(url_list: str):
    image = requests.get(url_list)
    if image.status_code == 200 and not image.content.startswith(b"<!DOCTYPE html>"):
        return image.content
    else:
        if "pesmaster" in url_list:
            return download_image(
                url_list.replace(
                    "https://www.pesmaster.com/efootball-2022/graphics/players/Variation2022/",
                    "https://efootballhub.net/images/efootball23/players/",
                )
            )
        elif "efootballhub" in url_list:
            raise ValueError
