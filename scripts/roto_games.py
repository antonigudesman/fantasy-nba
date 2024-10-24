import requests
from dateutil.parser import parse

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import Game
from general.compute import build_player_cache, build_TMS_cache

def get_games(data_source, data_source_id):
    # try:
        url = f'https://www.rotowire.com/daily/nba/api/slate-list.php?siteID={data_source_id}'
        print('=== Url:', url)
        games = requests.get(url).json()['games']

        if games:
            Game.objects.all().delete()

            for ii in games.values():
                defaults = {
                    'home_team': ii['homeTeamCode'],
                    'visit_team': ii['visitTeamCode'],
                    'ou': float(ii['overUnder']) if ii['overUnder'] else 0,
                    'date': parse(ii['gameDate'])
                }

                Game.objects.create(**defaults)

            build_TMS_cache()
            build_player_cache()
    # except:
    #     pass

if __name__ == "__main__":
    get_games('FanDuel', 2)
