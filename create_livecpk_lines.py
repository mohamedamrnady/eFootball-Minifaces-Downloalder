import os

names = os.listdir('temp/Minifaces')

with open('temp/sider.ini.txt', 'wb') as f:
    for name in names:
        f.write(str.encode('cpk.root = ".\livecpk\Minifaces\\' + name + '"'))
        f.write(b'\n')
    f.close()
