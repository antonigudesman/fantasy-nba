import requests

from bs4 import BeautifulSoup


def get_slate(ds):
    try:
        url = f'https://www.rotowire.com/daily/nba/api/slate-list.php?siteID={ds}'
        resp = requests.get(url).json()

        slate_id = resp['slates'][0]['slateID']
    except:
        slate_id = ''

    return slate_id
