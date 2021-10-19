# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
import json
import datetime

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Q
from django.forms.models import model_to_dict

from general.models import *
from general.lineup import Roster
from general.color import *
from general.utils import all_teams, current_season, formated_diff, mean, get_num_lineups
from general.compute import get_games_, get_ranking, generate_lineups, filter_players_fpa
from general.constants import (
    CSV_FIELDS, POSITION, SEASON_START_MONTH, SEASON_START_DAY,
    SEASON_END_MONTH, SEASON_END_DAY
)


def players(request):
    players = Player.objects.filter(data_source='FanDuel').order_by('first_name')
    return render(request, 'players.html', locals())


def lineup(request):
    data_sources = DATA_SOURCE
    games = Game.objects.all()
    return render(request, 'lineup.html', locals())


def download_game_report(request):
    game = request.GET.get('game')
    game = Game.objects.get(id=game)
    season = current_season()

    q = Q(team__in=[game.home_team, game.visit_team]) & \
        Q(opp__in=[game.home_team, game.visit_team]) & \
        Q(date__range=[datetime.date(season, SEASON_START_MONTH, SEASON_START_DAY), datetime.date(season+1, SEASON_END_MONTH, SEASON_END_DAY)])

    qs = PlayerGame.objects.filter(q)
    fields = [f.name for f in PlayerGame._meta.get_fields() 
              if f.name not in ['id', 'is_new']]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nba_games({}@{}).csv"'.format(game.visit_team, game.home_team)
    response['X-Frame-Options'] = 'GOFORIT'

    writer = csv.DictWriter(response, fields)
    writer.writeheader()

    for game in qs:
        game_ = model_to_dict(game, fields=fields)

        try:
            writer.writerow(game_)
        except Exception:
            print (game_)

    return response


@csrf_exempt
def fav_player(request):
    uid = request.POST.get('uid')
    if uid:
        if uid == "-1":
            request.session['fav'] = []
        else:
            fav = request.session.get('fav', [])
            if uid in fav:
                fav.remove(uid)
            else:
                fav.append(uid)
            request.session['fav'] = fav

    fav = request.session.get('fav', [])
    players = [Player.objects.filter(uid=uid).first() for uid in fav]
    players = sorted(players, key=Roster().position_order)

    return HttpResponse(render_to_string('fav-body.html', locals()))


@csrf_exempt
def get_players(request):
    ds = request.POST.get('ds')
    teams = request.POST.get('games').strip(';').replace(';', '-').split('-')
    players = Player.objects.filter(data_source=ds, 
                                    team__in=teams,
                                    play_today=True) \
                            .order_by('-proj_points')
    return HttpResponse(render_to_string('player-list_.html', locals()))


def player_detail(request, pid):
    player = Player.objects.get(id=pid)
    year = current_season()
    games = get_games_(pid, 'all', '', year)
    avg_min = games.aggregate(Avg('mp'))
    avg_fpts = games.aggregate(Avg('fpts'))

    return render(request, 'player_detail.html', locals())


@csrf_exempt
def player_games(request):
    pid = request.POST.get('pid')
    loc = request.POST.get('loc')
    opp = request.POST.get('opp')
    season = int(request.POST.get('season'))

    games = get_games_(pid, loc, opp, season)

    opps = '<option value="">All</option>'
    for ii in sorted(set(games.values_list('opp', flat=True).distinct())):
        opps += '<option>{}</option>'.format(ii)

    result = {
        'game_table': render_to_string('game-list_.html', locals()),
        'chart': [[ii.date.strftime('%Y/%m/%d'), ii.fpts] for ii in games],
        'opps': opps
    }

    return JsonResponse(result, safe=False)


def player_match_up_board(request):
    games = Game.objects.all()
    return render(request, 'player-match-up-board.html', locals())


def team_match_up_board(request):
    games = Game.objects.all()
    return render(request, 'team-match-up-board.html', locals())


@csrf_exempt
def team_match_up(request):
    min_afp = float(request.POST.get('min_afp'))
    max_afp = float(request.POST.get('max_afp'))

    game = request.POST.get('game')
    game = Game.objects.get(id=game)

    home_stat = TMSCache.objects.filter(team=game.home_team, type=2).first()
    away_stat = TMSCache.objects.filter(team=game.visit_team, type=2).first()

    teams = {
        'home': filter_players_fpa(game.home_team, min_afp, max_afp),
        'home_stat': json.loads(home_stat.body) if home_stat else {},
        'away': filter_players_fpa(game.visit_team, min_afp, max_afp),
        'away_stat': json.loads(away_stat.body) if away_stat else {}
    }

    return HttpResponse(render_to_string('team-board_.html', locals()))


@csrf_exempt
def player_match_up(request):
    loc = request.POST.get('loc')
    pos = request.POST.get('pos')
    pos = '' if pos == 'All' else pos
    ds = request.POST.get('ds')
    min_afp = float(request.POST.get('min_afp'))
    min_sfp = float(request.POST.get('min_sfp'))
    max_afp = float(request.POST.get('max_afp'))
    max_sfp = float(request.POST.get('max_sfp'))
    games = request.POST.get('games').strip(';').split(';')

    game_info = {}
    teams_ = []
    for game in games:
        teams = game.split('-') # home-away
        game_info[teams[0]] = [teams[1], '', '@']   # vs, loc, loc_
        game_info[teams[1]] = [teams[0], '@', '']

        if loc == '' or loc == 'all':
            teams_.append(teams[0])

        if loc == '@' or loc == 'all':
            teams_.append(teams[1])

    colors = linear_gradient('#90EE90', '#137B13', len(all_teams()))['hex']
    players = Player.objects.filter(data_source=ds, play_today=True, team__in=teams_) \
                            .order_by('-proj_points')
    players_ = []
    for player in players:
        position = player.actual_position.split('/')[0] if player.position == 'UT' else player.position
        if pos in position:
            if min_afp <= player.afp <= max_afp:
                if min_sfp <= player.sfp <= max_sfp:
                    vs = game_info[player.team][0]
                    loc = game_info[player.team][1]
                    loc_ = game_info[player.team][2]

                    opr_info_ = json.loads(TMSCache.objects.filter(team=vs, type=2).first().body)

                    players_.append({
                        'avatar': player.avatar,
                        'id': player.id,
                        'uid': player.uid,
                        'name': '{} {}'.format(player.first_name, player.last_name),
                        'team': player.team,
                        'loc': loc,
                        'vs': vs,
                        'pos': position,
                        'inj': player.injury,
                        'salary': player.salary,
                        'ampg': player.ampg,
                        'smpg': player.smpg,
                        'mdiff': formated_diff(player.smpg-player.ampg,),
                        'afp': player.afp,
                        'sfp': player.sfp,
                        'pdiff': formated_diff(player.sfp-player.afp),
                        'val': player.salary / 250 + 10,    # exception
                        'opp': opr_info_[position],
                        'opr': opr_info_[position+'_rank'],
                        'color': colors[opr_info_[position+'_rank']-1]
                    })

    groups = { ii: [] for ii in POSITION }
    for ii in players_:
        groups[ii['pos']].append(ii)

    num_oprs = []
    for ii in POSITION:
        if groups[ii]:
            groups[ii], _ = get_ranking(groups[ii], 'sfp', 'ppr', -1)
            groups[ii] = sorted(groups[ii], key=lambda k: k['team'])
            groups[ii] = sorted(groups[ii], key=lambda k: -k['opr'])

    players = []
    for ii in POSITION:
        if groups[ii]:
            players += groups[ii] + [{}]

    return HttpResponse(render_to_string('player-board_.html', locals()))


@csrf_exempt
def gen_lineups(request):
    lineups, players = generate_lineups(request)
    avg_points = mean([ii.projected() for ii in lineups])

    players_ = [{ 'name': '{} {}'.format(ii.first_name, ii.last_name), 
                  'team': ii.team, 
                  'id': ii.id, 
                  'avatar': ii.avatar, 
                  'lineups': get_num_lineups(ii, lineups)} 
                for ii in players if get_num_lineups(ii, lineups)]
    players_ = sorted(players_, key=lambda k: k['lineups'], reverse=True)

    return HttpResponse(render_to_string('player-lineup.html', locals()))


def export_lineups(request):
    lineups, _ = generate_lineups(request)

    ds = request.POST.get('ds')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fantasy_nba_{}.csv"'.format(ds.lower())
    response['X-Frame-Options'] = 'GOFORIT'

    header = CSV_FIELDS[ds]
    writer = csv.writer(response)
    writer.writerow(header)

    for ii in lineups:
        writer.writerow(ii.get_csv(ds))

    return response


@csrf_exempt
def update_point(request):
    pid = int(request.POST.get('pid'))
    points = request.POST.get('val')

    cus_proj = request.session.get('cus_proj', {})
    cus_proj[pid] = points
    request.session['cus_proj'] = cus_proj

    return HttpResponse('')
