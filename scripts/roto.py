import requests

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import Player
from general.constants import DATA_SOURCE
from scripts.get_slate import get_slate


def get_players(data_source, data_source_id):
    try:
        slate_id = get_slate(data_source_id)
        url = f'https://www.rotowire.com/daily/nba/api/players.php?slateID={slate_id}'
        print(url)

        players = requests.get(url).json()
        print (data_source, len(players))

        for ii in players:
            try:
                pos = ii['pos']
                defaults = {
                    'play_today': True,
                    'first_name': ii['firstName'],
                    'last_name': ii['lastName'],
                    'position': pos[0],
                    'opponent': ii['opponent']['team'],
                    'proj_points': ii['pts'],
                    'actual_position': '/'.join(pos),
                    'salary': ii['salary'],
                    'team': ii['team']['abbr'],
                    'injury': ii['injuryStatus'] or '',
                    'avatar': ii['imageURL'],
                }

                Player.objects.update_or_create(uid=ii['rwID'], data_source=data_source, defaults=defaults)
            except Exception as e:
                pass
    except:
        print('*** Something is wrong ***')


if __name__ == "__main__":
    Player.objects.all().update(play_today=False)

    for id, ds in enumerate(DATA_SOURCE, 1):
        get_players(ds[0], id)
