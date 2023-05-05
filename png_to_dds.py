import os
from typing import List
from wand import image


def get_pngs():
    all_pngs = []
    all_items = os.listdir(os.getcwd())
    for item in all_items:
        if item.find('.png') != -1:
            all_pngs.append(item)
    return all_pngs


def get_dds(all_pngs: List, pes_version: int = 21):
    all_dds = []
    for png in all_pngs:
        dds = png.replace('png', 'dds')
        if pes_version == 17:
            dds = 'player_' + dds
        all_dds.append(dds)
    return all_dds


def png_to_dds(pes_version: int = 21):
    all_pngs = get_pngs()
    all_dds = get_dds(all_pngs, pes_version)
    for counter, png in enumerate(all_pngs):
        try:
            with image.Image(filename=png) as img:
                img.compression = "dxt3"
                img.save(filename=all_dds[counter])
        except:
            print(f"Couldn't read {png}")


def sort_all_images(league_name, pes_version: int = 21):
    all_pngs = get_pngs()
    if all_pngs != []:
        if os.path.exists('temp/Minifaces') == False:
            os.makedirs('temp/Minifaces')
        league_name = os.path.join(
            'temp/Minifaces', league_name, 'common/render/symbol/player')
        if os.path.exists('PNG') == False:
            os.mkdir('PNG')
        if os.path.exists(league_name) == False:
            os.makedirs(league_name)
        for png in all_pngs:
            try:
                os.rename(png, os.path.join('PNG', png))
            except:
                os.remove(os.path.join('PNG', png))
                os.rename(png, os.path.join('PNG', png))
        for dds in get_dds(all_pngs, pes_version):
            try:
                os.rename(dds, os.path.join(league_name, dds))
            except:
                os.remove(os.path.join(league_name, dds))
                os.rename(dds, os.path.join(league_name, dds))
