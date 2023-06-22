import requests
from bs4 import BeautifulSoup as bs

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}


def miniface_downloader(url: str):
    all_pictures = []
    r = requests.get(url, headers=headers)
    soup = bs(r.content, "html.parser")

    cards_div = soup.find_all("div", attrs={"class": "player-card-container"})

    try:
        cards_div = cards_div[len(cards_div) - 1].find_all(
            "figure", attrs={"class": "player-card efootball-2022"}
        )
        for cards in cards_div:
            pictures_div = cards.find_all("img")
            for pictures in pictures_div:
                if pictures["data-src"].find("Variation2022") != -1:
                    picture_url = "https://www.pesmaster.com" + pictures["data-src"]
                    picture_name = str(
                        picture_url.split("/Variation2022/")[1].split("/")[0]
                    )
                    if (
                        picture_name.find("b") == -1
                        and picture_name.find("dummy") == -1
                    ):
                        all_pictures.append(picture_url)
        image_bytes = download_image(all_pictures)
        if len(all_pictures) != 0:
            open(str(url.split("/player/")[1].split("/")[0]) + ".png", "wb").write(
                image_bytes
            )
    except:
        pass


def download_image(url_list: list):
    if len(url_list) > 0:
        image = requests.get(url_list[len(url_list) - 1])
        if (
            image.status_code == 200
            and image.content.startswith(b"<!DOCTYPE html>") == False
        ):
            return image.content
        else:
            if "pesmaster" in url_list[len(url_list) - 1]:
                url_list[len(url_list) - 1] = url_list[len(url_list) - 1].replace(
                    "https://www.pesmaster.com/efootball-2022/graphics/players/Variation2022/",
                    "https://efootballhub.net/images/efootball23/players/",
                )
            elif "efootballhub" in url_list[len(url_list) - 1]:
                url_list.pop()
            return download_image(url_list)
    else:
        raise ValueError
