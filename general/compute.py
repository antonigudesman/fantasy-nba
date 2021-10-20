import json
import datetime

from django.db.models import Avg, Q, Sum

from general.models import Player, PlayerGame, Game, TMSCache
from general.constants import (
    POSITION, SEASON_START_MONTH, SEASON_START_DAY,
    SEASON_END_MONTH, SEASON_END_DAY
)
from general.utils import current_season, all_teams, get_player
from general.lineup import Roster, calc_lineups


def generate_lineups(request):
    ids = request.POST.getlist('ids')
    locked = request.POST.getlist('locked')
    num_lineups = int(request.POST.get('num-lineups'))
    ds = request.POST.get('ds')

    ids = [int(ii) for ii in ids]
    locked = [int(ii) for ii in locked]

    players = Player.objects.filter(id__in=ids)
    lineups = calc_lineups(players, num_lineups, locked, ds)

    return lineups, players


def get_games_(pid, loc, opp, season):
    player = Player.objects.get(id=pid)
    q = Q(name='{} {}'.format(player.first_name, player.last_name)) \
      & Q(date__range=[datetime.date(season, SEASON_START_MONTH, SEASON_START_DAY), datetime.date(season+1, SEASON_END_MONTH, SEASON_END_DAY)])

    if opp:
        q &= Q(opp=opp)
    if loc != 'all':
        q &= Q(location=loc)

    return PlayerGame.objects.filter(q).order_by('-date')


def get_ranking(players, sattr, dattr, order=1):
    # order = 1: ascending, -1: descending
    players = sorted(players, key=lambda k: k[sattr]*order)
    ranking = 0
    prev_val = None
    for ii in players:
        if ii[sattr] != prev_val:
            prev_val = ii[sattr]
            ranking += 1
        ii[dattr] = ranking
    return players, ranking


def get_team_games(team):
    # get all games for the team last season
    players_ = Player.objects.filter(team=team, data_source='FanDuel')
    players_ = ['{} {}'.format(ip.first_name, ip.last_name) for ip in players_]

    season = current_season()
    q = Q(name__in=players_) & \
        Q(date__range=[datetime.date(season, SEASON_START_MONTH, SEASON_START_DAY), datetime.date(season+1, SEASON_END_MONTH, SEASON_END_DAY)])

    return PlayerGame.objects.filter(q)


def get_team_stat(team, loc):
    loc_ = '@' if loc == '' else ''
    # allowance
    season = current_season()
    q = Q(opp=team) & Q(location=loc_) & \
        Q(date__range=[datetime.date(season, SEASON_START_MONTH, SEASON_START_DAY), datetime.date(season+1, SEASON_END_MONTH, SEASON_END_DAY)])
    a_teams = PlayerGame.objects.filter(q)
    a_teams_ = a_teams.values('date').annotate(trb=Sum('trb'), 
                                               ast=Sum('ast'),
                                               stl=Sum('stl'),
                                               blk=Sum('blk'),
                                               tov=Sum('tov'),
                                               pts=Sum('pts'))

    rpg = a_teams_.aggregate(Avg('trb'))['trb__avg'] or 0
    apg = a_teams_.aggregate(Avg('ast'))['ast__avg'] or 0
    spg = a_teams_.aggregate(Avg('stl'))['stl__avg'] or 0
    bpg = a_teams_.aggregate(Avg('blk'))['blk__avg'] or 0
    tov = a_teams_.aggregate(Avg('tov'))['tov__avg'] or 0
    ppg = a_teams_.aggregate(Avg('pts'))['pts__avg'] or 0

    # score
    q = Q(team=team) & Q(location=loc) & \
        Q(date__range=[datetime.date(season, SEASON_START_MONTH, SEASON_START_DAY), datetime.date(season+1, SEASON_END_MONTH, SEASON_END_DAY)])
    s_teams = PlayerGame.objects.filter(q)
    s_teams_ = s_teams.values('date').annotate(trb=Sum('trb'), 
                                               ast=Sum('ast'),
                                               stl=Sum('stl'),
                                               blk=Sum('blk'),
                                               tov=Sum('tov'),
                                               pts=Sum('pts'))

    s_rpg = s_teams_.aggregate(Avg('trb'))['trb__avg'] or 0 
    s_apg = s_teams_.aggregate(Avg('ast'))['ast__avg'] or 0
    s_spg = s_teams_.aggregate(Avg('stl'))['stl__avg'] or 0
    s_bpg = s_teams_.aggregate(Avg('blk'))['blk__avg'] or 0
    s_tov = s_teams_.aggregate(Avg('tov'))['tov__avg'] or 0
    s_ppg = s_teams_.aggregate(Avg('pts'))['pts__avg'] or 0

    res = {
        'team': team,
        'rpg': rpg,
        'apg': apg,
        'spg': spg,
        'bpg': bpg,
        'tov': tov,
        'ppg': ppg,
        'total': rpg+apg+spg+bpg+tov+ppg,
        's_rpg': s_rpg,
        's_apg': s_apg,
        's_spg': s_spg,
        's_bpg': s_bpg,
        's_tov': s_tov,
        's_ppg': s_ppg,
        's_total': s_rpg+s_apg+s_spg+s_bpg+s_tov+s_ppg
    }

    # FPA TM POS
    tm_pos = []
    # for each distinct match
    for ii in a_teams_:
        # players (games) in a match
        players = a_teams.filter(date=ii['date'])

        tm_pos_ = {}
        # for each position
        for pos in POSITION:
            # players in the position of the team
            q = Q(position=pos) & Q(data_source='FanDuel')
            players_ = Player.objects.filter(Q(team=players[0].team) & q)
            players_ = ['{} {}'.format(ip.first_name, ip.last_name) for ip in players_]
            tm_pos_[pos] = players.filter(name__in=players_).aggregate(Sum('fpts'))['fpts__sum'] or 0
        if tm_pos_['PG'] > 0 and tm_pos_['SG'] > 0:
            tm_pos.append(tm_pos_)
        print (ii['date'], players[0].team, players[0].opp, players[0].location, tm_pos_)
        
    for pos in POSITION:
        res[pos] = sum(ii[pos] for ii in tm_pos) / len(tm_pos) if len(tm_pos) else -1

    print ('-'*32)
    # for FPS TM POS
    tm_pos = []
    # for each distinct match
    for ii in s_teams_:
        # players (games) in a match
        players = s_teams.filter(date=ii['date'])

        tm_pos_ = {}
        # for each position
        for pos in POSITION:
            # players in the position of the team
            q = Q(position=pos) & Q(data_source='FanDuel')
            players_ = Player.objects.filter(Q(team=players[0].team) & q)
            players_ = ['{} {}'.format(ip.first_name, ip.last_name) for ip in players_]
            tm_pos_[pos] = players.filter(name__in=players_).aggregate(Sum('fpts'))['fpts__sum'] or 0
        if tm_pos_['PG'] > 0 and tm_pos_['SG'] > 0:
            tm_pos.append(tm_pos_)
        print (ii['date'], players[0].team, players[0].opp, players[0].location, tm_pos_)

    print ('-'*32)
    for pos in POSITION:
        res['s_'+pos] = sum(ii[pos] for ii in tm_pos) / len(tm_pos) if len(tm_pos) else -1

    return res


def get_win_loss(team):
    season = current_season()
    q = Q(team=team) & \
        Q(date__range=[datetime.date(season, SEASON_START_MONTH, SEASON_START_DAY), datetime.date(season+1, SEASON_END_MONTH, SEASON_END_DAY)])

    team_games = PlayerGame.objects.filter(q)
    game_results = team_games.values('date', 'game_result').distinct()
    wins = game_results.filter(game_result='W').count()
    losses = game_results.filter(game_result='L').count()

    return wins, losses


def get_team_info(team, loc):
    team_games = get_team_games(team)
    # at most one game a day
    wins, losses = get_win_loss(team)

    # get distinct players
    players_ = team_games.values('name').distinct()

    players = []

    for ii in players_:
        player = get_player(ii['name'])
        if player:
            games = team_games.filter(name=ii['name'], location=loc)
            ampg = games.aggregate(Avg('mp'))['mp__avg']
            afp = games.aggregate(Avg('fpts'))['fpts__avg']

            l3a = sum([ig.fpts for ig in games.order_by('-date')[:3]]) / 3
            value = player.salary / 250 + 10

            # update l3a for the player
            Player.objects.filter(uid=player.uid).update(l3a=l3a)

            players.append({
                'avatar': player.avatar,
                'id': player.id,
                'uid': player.uid,
                'name': ii['name'],
                'pos': player.position,
                'inj': player.injury,
                'salary': player.salary,
                'gp': games.count(),
                'rpg': games.aggregate(Avg('trb'))['trb__avg'],
                'apg': games.aggregate(Avg('ast'))['ast__avg'],
                'spg': games.aggregate(Avg('stl'))['stl__avg'],
                'bpg': games.aggregate(Avg('blk'))['blk__avg'],
                'ppg': games.aggregate(Avg('pts'))['pts__avg'],
                'tov': games.aggregate(Avg('tov'))['tov__avg'],
                'ampg': ampg,
                'afp': afp,
                'sfp': l3a,
                'val': value
            })

    return { 
        'players': sorted(players, key=Roster().dict_position_order), 
        'wins': wins,
        'losses': losses,
        'win_percent': wins * 100.0 / (wins + losses) if wins + losses > 0 else 0
    }


def filter_players_fpa(team, min_afp, max_afp):
    try:
        info = json.loads(TMSCache.objects.filter(team=team, type=1).first().body)
        players = []

        for ii in range(len(info['players'])):
            afp = info['players'][ii]['afp']
            if min_afp <= afp <= max_afp:
                players.append(info['players'][ii])
        info['players'] = players
        return info
    except Exception as e:
        return {}


def build_player_cache():
    # player info -> build cache
    players = Player.objects.filter(data_source='FanDuel', play_today=True) \
                            .order_by('-proj_points')
    game_info = {}
    for game in Game.objects.all():
        game_info[game.home_team] = ''
        game_info[game.visit_team] = '@'

    for player in players:
        games = get_games_(player.id, 'all', '', current_season())
        ampg = games.aggregate(Avg('mp'))['mp__avg'] or 0
        smpg = games.filter(location=game_info[player.team]).aggregate(Avg('mp'))['mp__avg'] or 0
        afp = games.aggregate(Avg('fpts'))['fpts__avg'] or 0
        sfp = games.filter(location=game_info[player.team]).aggregate(Avg('fpts'))['fpts__avg'] or 0

        Player.objects.filter(uid=player.uid).update(
            ampg=ampg,
            smpg=smpg,
            afp=afp,
            sfp=sfp,
            value=player.salary / 250 + 10
        )


def build_TMS_cache():
    stat_home = [get_team_stat(ii, '') for ii in all_teams()]
    stat_away = [get_team_stat(ii, '@') for ii in all_teams()]

    attrs = list(stat_home[0].keys())
    for attr in attrs:
        if attr != 'team':
            order = -1 if attr.startswith('s_') else 1
            stat_home, _ = get_ranking(stat_home, attr, attr+'_rank', order)
            stat_away, _ = get_ranking(stat_away, attr, attr+'_rank', order)

    stat_home = { ii['team']: ii for ii in stat_home }
    stat_away = { ii['team']: ii for ii in stat_away }

    team_info = {}
    for game in Game.objects.all():
        team_info[game.home_team] = get_team_info(game.home_team, '')
        team_info[game.visit_team] = get_team_info(game.visit_team, '@')

    TMSCache.objects.all().delete()

    TMSCache.objects.create(team='STAT_HOME', type=3, body=json.dumps(stat_home))
    TMSCache.objects.create(team='STAT_AWAY', type=3, body=json.dumps(stat_away))

    for game in Game.objects.all():
        TMSCache.objects.create(team=game.home_team, type=1, body=json.dumps(team_info[game.home_team]))
        TMSCache.objects.create(team=game.visit_team, type=1, body=json.dumps(team_info[game.visit_team]))
        TMSCache.objects.create(team=game.home_team, type=2, body=json.dumps(stat_home[game.home_team]))
        TMSCache.objects.create(team=game.visit_team, type=2, body=json.dumps(stat_away[game.visit_team]))
