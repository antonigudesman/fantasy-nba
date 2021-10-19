import os
import csv
import datetime
import mimetypes

from wsgiref.util import FileWrapper

from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.forms.models import model_to_dict

from general.models import Player
from general.constants import SEASON_START_MONTH, SEASON_START_DAY


def _all_teams():
    return [ii['team'] for ii in Player.objects.values('team').distinct()]


def current_season():
    today = datetime.date.today()
    return today.year if today > datetime.date(today.year, SEASON_START_MONTH, SEASON_START_DAY) else today.year - 1


def formated_diff(val):
    fm = '{:.1f}' if val > 0 else '({:.1f})'
    return fm.format(abs(val))


def get_player(full_name):
    '''
    FanDuel has top priority
    '''
    names = full_name.split(' ')
    players = Player.objects.filter(first_name=names[0], last_name=names[1]) \
                            .order_by('data_source')
    return players.filter(data_source='FanDuel').first()


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def get_num_lineups(player, lineups):
    num = 0
    for ii in lineups:
        if ii.is_member(player):
            num = num + 1
    return num


def download_response(queryset, path, result_csv_fields):
    result = open(path, 'w')
    result_csv = csv.DictWriter(result, fieldnames=result_csv_fields)
    result_csv.writeheader()

    for game in queryset:
        game_ = model_to_dict(game, fields=result_csv_fields)

        try:
            result_csv.writerow(game_)
        except Exception:
            print (game_)

    result.close()

    wrapper = FileWrapper( open( path, "r" ) )
    content_type = mimetypes.guess_type( path )[0]

    response = HttpResponse(wrapper, content_type = content_type)
    response['Content-Length'] = os.path.getsize( path ) 
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str( os.path.basename( path ) ) 

    return response
