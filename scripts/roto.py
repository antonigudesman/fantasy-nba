import requests

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import Player
from general.constants import DATA_SOURCE
from general import html2text
from scripts.get_slate import get_slate


def get_players(data_source, data_source_id):
    try:
        slate_id = get_slate(data_source)
        url = 'https://www.rotowire.com/daily/tables/optimizer-nba.php' + \
              '?siteID={}&slateID={}&projSource=RotoWire&oshipSource=RotoWire'.format(data_source_id, slate_id)
        print(url)

        players = requests.get(url).json()

        fields = ['first_name', 'last_name', 'position', 'opponent', 'proj_points',
                  'actual_position', 'salary', 'team']
        print (data_source, len(players))
        for ii in players:
            try:
                defaults = { key: str(ii[key]).replace(',', '') for key in fields }
                defaults['play_today'] = True

                defaults['injury'] = html2text.html2text(ii['injury']).strip()
                if data_source == 'FantasyDraft':
                    defaults['position'] = defaults['actual_position']
                Player.objects.update_or_create(uid=ii['id'], data_source=data_source, defaults=defaults)
            except Exception as e:
                pass
    except:
        print('*** Something is wrong ***')


if __name__ == "__main__":
    Player.objects.all().update(play_today=False)
    for id, ds in enumerate(DATA_SOURCE, 1):
        get_players(ds[0], id)
