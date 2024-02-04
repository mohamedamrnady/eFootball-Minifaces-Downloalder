import os
import requests
from bs4 import BeautifulSoup as bs
from wand import image

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}


def miniface_downloader(url: str, isUpdate=False):
    images_downloaded = []
    image_name = str(url.split("/player/")[1].split("/")[0])
    teams_dir = os.path.join(image_name, "map_teams.csv")
    if isUpdate:
        image_name = str(
            int(
                hex(int(image_name))[-6:],
                base=16,
            )
        )
        teams_dir = os.path.join(image_name, "map_teams.csv")
        try:
            written_teams = open(teams_dir).readlines()
        except FileNotFoundError:
            written_teams = []
    else:
        written_teams = []
    r = requests.get(url, headers=headers)
    soup = bs(r.content, "html.parser")

    cards_div = soup.find_all("div", attrs={"class": "player-card-container"})

    try:
        cards_div = cards_div[len(cards_div) - 1].find_all(
            "figure", attrs={"class": "player-card efootball-2022"}
        )
        if isUpdate:
            cards_div = [
                soup.find_all("figure", attrs={"class": "player-card efootball-2022"})[
                    0
                ]
            ]

        for i, cards in enumerate(cards_div):
            images_downloaded.append(
                {
                    "team": "",
                }
            )
            pictures_div = cards.find_all("img")
            for pictures in pictures_div:
                if "teamlogos" in pictures["data-src"]:
                    images_downloaded[i]["team"] = str(
                        int(
                            pictures["data-src"]
                            .split("/teamlogos/")[1]
                            .split("/")[0]
                            .replace(".png", "")
                            .replace("e_", "")
                            .replace("_w", "")
                        )
                    )
                elif "graphics/players" in pictures["data-src"]:
                    picture_url = "https://www.pesmaster.com" + pictures["data-src"]
                    if "/Variation2022/" in pictures["data-src"]:
                        picture_name = str(
                            picture_url.split("/Variation2022/")[1].split("/")[0]
                        )
                        images_downloaded[i]["default"] = False
                    else:
                        picture_name = str(
                            picture_url.split("graphics/players/")[1].split("/")[0]
                        )
                        images_downloaded[i]["default"] = True
                    if not "b" in picture_name and not "dummy" in picture_name:
                        if not images_downloaded[i]["default"]:
                            images_downloaded[i]["bytes"] = download_image(picture_url)
                        else:
                            images_downloaded[i]["bytes"] = False
                        images_downloaded[i]["id"] = picture_name.replace("_.png", "")

        if len(images_downloaded) != 0:
            if not os.path.exists(image_name):
                os.makedirs(image_name)
            with open(teams_dir, "a") as f:
                for image_downloaded in images_downloaded:
                    if image_downloaded["bytes"]:
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
        print(f"Skipped {url} : {e}")


def download_image(url: str):
    image = requests.get(url)
    if image.status_code == 200 and not image.content.startswith(b"<!DOCTYPE html>"):
        return image.content
    else:
        if "pesmaster" in url:
            return download_image(
                url.replace(
                    "https://www.pesmaster.com/efootball-2022/graphics/players/Variation2022/",
                    "https://efootballhub.net/images/efootball23/players/",
                )
            )
        elif "efootballhub" in url:
            print(f"Skipped {url}")
            return False
