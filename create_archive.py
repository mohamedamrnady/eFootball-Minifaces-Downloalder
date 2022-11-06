import shutil
from datetime import date


shutil.make_archive("PES 2021 Featured Players' Minifaces - " +
                    date.today() + " Update", 'zip', "temp")
