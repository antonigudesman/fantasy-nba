import csv
import datetime

from django.http import HttpResponse

from general.models import Player
from general.constants import SEASON_START_MONTH, SEASON_START_DAY


def all_teams():
    return [ii['team'] for ii in Player.objects.values('team').distinct()]


def current_season():
    today = datetime.date.today()
    compare_date = datetime.date(today.year, SEASON_START_MONTH, SEASON_START_DAY)

    return today.year if today > compare_date else today.year - 1


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
    return sum([1 for ii in lineups if ii.is_member(player)])


def download_response(header, data, filename):
    '''
    :param: header: list(str)
    :param: data: list(dict)
    '''
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response['X-Frame-Options'] = 'GOFORIT'

    writer = csv.DictWriter(response, header)
    writer.writeheader()

    for entity in data:
        writer.writerow(entity)

    return response
