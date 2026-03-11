import os

from os import sys, path
from datetime import datetime
from dateutil.parser import parse

import django
import requests

from pytz import timezone


sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import Game
from general.compute import build_player_cache, build_TMS_cache

def get_games(data_source, data_source_id):
    try:
        url = f'https://www.rotowire.com/daily/nba/api/slate-list.php?siteID={data_source_id}'
        print('=== Url:', url)
        games = requests.get(url).json()['games']

        if games:
            Game.objects.all().delete()
            pst = timezone('US/Pacific')
            today = datetime.now(pst).strftime('%Y-%m-%d')

            for ii in games.values():
                if not ii['gameDate'].startswith(today):
                     continue

                defaults = {
                    'home_team': ii['homeTeamCode'],
                    'visit_team': ii['visitTeamCode'],
                    'ou': float(ii['overUnder']) if ii['overUnder'] else 0,
                    'date': parse(ii['gameDate'])
                }

                Game.objects.create(**defaults)

            build_TMS_cache()
            build_player_cache()
    except:
        pass

if __name__ == "__main__":
    get_games('FanDuel', 2)
