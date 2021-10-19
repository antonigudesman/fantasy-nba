from django.conf.urls import url
from django.contrib import admin

from general.views import *

admin.site.site_header = "Fantasy NBA"

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', players, name="players"),
    url(r'^lineup$', lineup, name="lineup"),
    url(r'^fav-player$', fav_player, name="fav_player"),
    url(r'^players/(?P<pid>\d+)$', player_detail, name="player_detail"),
    url(r'^gen-lineups', gen_lineups, name="gen_lineups"),
    url(r'^get-players', get_players, name="get_players"),
    url(r'^export-lineups', export_lineups, name="export_lineups"),
    url(r'^update-point', update_point, name="update_point"),
    url(r'^player-games', player_games, name="player_games"),
    url(r'^player-match-up-board', player_match_up_board, name="player_match_up_board"),
    url(r'^player-match-up', player_match_up, name="player_match_up"),
    url(r'^team-match-up-board', team_match_up_board, name="team_match_up_board"),
    url(r'^team-match-up', team_match_up, name="team_match_up"),
    url(r'^download-game-report', download_game_report, name="download_game_report"),
]
