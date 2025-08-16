import os
import requests
from bs4 import BeautifulSoup as bs
from wand import image

downloaded_events = {"names": [], "bytes": []}


def miniface_downloader(card, player_id=False):
    image_dict = {
        "team": "",
        "default": True,
        "bytes": False,
        "id": "",
        "background_bytes": False,
    }
    pictures_div = card.find_all("img")
    for pictures in pictures_div:
        if "teamlogos" in pictures["data-src"]:
            image_dict["team"] = str(
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
                    picture_url.split("/Variation2022/")[-1].split("/")[0]
                )
                image_dict["default"] = False
            else:
                picture_name = str(
                    picture_url.split("graphics/players/")[-1].split("/")[0]
                )
                image_dict["default"] = True
            if not "b" in picture_name and not "dummy" in picture_name:
                if not image_dict["default"]:
                    image_dict["bytes"] = download_image(picture_url)
                else:
                    image_dict["bytes"] = False
                image_dict["id"] = picture_name.replace("_.png", "")
            elif "_b02" in picture_name:
                image_dict["background_bytes"] = get_card_event(
                    picture_name, picture_url
                )
    if not player_id:
        player_id = str(
            int(
                hex(int(image_dict["id"].split("/player/")[-1].split("/")[0]))[-6:],
                base=16,
            )
        )

    if not os.path.exists(player_id):
        os.makedirs(player_id)
        if image_dict["bytes"]:
            dirc = os.path.join(player_id, image_dict["team"])
            if not os.path.exists(dirc):
                os.makedirs(dirc)
            fn = os.path.join(
                dirc,
                image_dict["id"] + ".dds",
            )
            back_img = image.Image(
                blob=image_dict["background_bytes"],
            )
            fore_img = image.Image(
                blob=image_dict["bytes"],
            )
            back_img.trim(percent_background=0.5)
            back_img.resize(fore_img.width, fore_img.height)
            back_img.composite(fore_img)
            back_img.compression = "dxt5"
            back_img.save(filename=fn)


def download_image(url: str):
    r = requests.get(url)
    if r.status_code == 200 and not r.content.startswith(b"<!DOCTYPE html>"):
        return r.content
    else:
        if "pesmaster" in url:
            return download_image(
                url.replace(
                    "https://www.pesmaster.com/efootball-2022/graphics/players/Variation2022/",
                    "https://efootballhub.net/images/efootball23/players/",
                )
            )
        elif "efootball23" in url:
            return download_image(
                url.replace(
                    "efootball23",
                    "efootball24",
                )
            )
        elif "efootball24" in url:
            print(f"Skipped {url}")
            return False


def get_card_event(event_name, event_url):
    if event_name in downloaded_events["names"]:
        return downloaded_events["bytes"][downloaded_events["names"].index(event_name)]
    else:
        downloaded_events["names"].append(event_name)
        b = download_image(event_url)
        downloaded_events["bytes"].append(b)
        return b
