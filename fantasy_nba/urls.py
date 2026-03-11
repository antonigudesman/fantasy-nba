from django.urls import path
from django.contrib import admin

from general.views import *

admin.site.site_header = "Fantasy NBA"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', players, name="players"),
    path('lineup', lineup, name="lineup"),
    path('fav-player', fav_player, name="fav_player"),
    path('players/<int:pid>', player_detail, name="player_detail"),
    path('gen-lineups', gen_lineups, name="gen_lineups"),
    path('get-players', get_players, name="get_players"),
    path('export-lineups', export_lineups, name="export_lineups"),
    path('update-point', update_point, name="update_point"),
    path('player-games', player_games, name="player_games"),
    path('player-match-up-board', player_match_up_board, name="player_match_up_board"),
    path('player-match-up', player_match_up, name="player_match_up"),
    path('team-match-up-board', team_match_up_board, name="team_match_up_board"),
    path('team-match-up', team_match_up, name="team_match_up"),
    path('download-game-report', download_game_report, name="download_game_report"),
]
