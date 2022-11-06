import os

os.chdir('Minifaces')

names = os.listdir()

with open('sider.ini.txt', 'wb') as f:
    for name in names:
        f.write(str.encode('cpk.root = ".\livecpk\Minifaces\\' + name + '"'))
        f.write(b'\n')
    f.close()
