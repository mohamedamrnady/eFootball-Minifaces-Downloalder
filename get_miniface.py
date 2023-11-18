import requests
from bs4 import BeautifulSoup as bs

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}


def reverse_hex(a):
    return "".join(reversed([a[i : i + 2] for i in range(0, len(a), 2)]))


def miniface_downloader(url: str, isUpdate=False):
    all_pictures = []
    player_ids = []
    pictures_versions = []
    r = requests.get(url, headers=headers)
    soup = bs(r.content, "html.parser")

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
                        player_ids.append(int(picture_name.replace("_.png", "")))
                        pictures_versions.append(
                            int(
                                reverse_hex(
                                    hex(int(picture_name.replace("_.png", "")))[:-6][
                                        -4:
                                    ],
                                ),
                                base=16,
                            )
                        )
        if isUpdate:
            image_bytes = download_image([all_pictures[0]], [pictures_versions[0]])
        else:
            image_bytes = download_image(all_pictures, pictures_versions)
        if len(all_pictures) != 0:
            if isUpdate:
                image_name = str(
                    int(
                        hex(player_ids[0])[-6:],
                        base=16,
                    )
                )
            else:
                image_name = str(url.split("/player/")[1].split("/")[0])
            open(image_name + ".png", "wb").write(image_bytes)
    except Exception as e:
        print(f"Skipped {url}: {e}")


def download_image(url_list: list, versions: list):
    if len(url_list) > 0:
        index = versions.index(max(versions))
        image = requests.get(url_list[index])
        if (
            image.status_code == 200
            and image.content.startswith(b"<!DOCTYPE html>") == False
        ):
            return image.content
        else:
            if "pesmaster" in url_list[index]:
                url_list[index] = url_list[index].replace(
                    "https://www.pesmaster.com/efootball-2022/graphics/players/Variation2022/",
                    "https://efootballhub.net/images/efootball23/players/",
                )
            elif "efootballhub" in url_list[index]:
                del url_list[index]
                del versions[index]
            return download_image(url_list, versions)
    else:
        raise ValueError
