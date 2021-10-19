import requests
import datetime

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import Game
from general.compute import build_player_cache, build_TMS_cache
from scripts.get_slate import get_slate

def get_games(data_source, data_source_id):
    # try:
        slate_id = get_slate(data_source)
        url = 'https://www.rotowire.com/daily/tables/nba/schedule.php' + \
            '?siteID={}&slateID={}'.format(data_source_id, slate_id)
        print('=== Url:', url)
        games = requests.get(url).json()

        if games:
            Game.objects.all().delete()
            fields = ['ml', 'home_team', 'visit_team']
            for ii in games:
                defaults = { key: str(ii[key]).replace(',', '') for key in fields }
                defaults['date'] = datetime.datetime.strptime(ii['date'][5:], '%I:%M %p')
                # date is not used
                defaults['date'] = datetime.datetime.combine(datetime.date.today(), defaults['date'].time())
                defaults['ou'] = float(ii['ou']) if ii['ou'] else 0
                Game.objects.create(**defaults)
            build_TMS_cache()
            build_player_cache()
    # except:
    #     pass

if __name__ == "__main__":
    get_games('FanDuel', 2)
