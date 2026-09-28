# -*- coding: utf-8 -*-
"""משחק חדש ומעבר בין שלבים."""

from ..models import GameState, Inventory, MissionKind, Player
from ..world import START_TILE, build_level, tile_center
from . import missions

START_WEAPON = "glock19"
START_AMMO = {"ammo_pistol": 80}          # מלאי התחלתי לגלוק
SPAWN_INVULN_FRAMES = 60


def new_game() -> GameState:
    x, y = tile_center(*START_TILE)
    state = GameState(
        player=Player(x=x, y=y),
        inventory=Inventory(weapons=[START_WEAPON], ammo=dict(START_AMMO)),
        level=build_level(1),
    )
    _place_player(state)
    missions.assign(state)
    return state


def enter_level(state: GameState, number: int) -> None:
    state.level = build_level(number)
    state.inspect_uid = None
    _place_player(state)
    missions.assign(state)


def leave_level(state: GameState) -> None:
    state.play("level")
    exit_mission = state.mission is not None and state.mission.kind == MissionKind.EXIT
    missions.progress(state, MissionKind.EXIT)
    enter_level(state, state.level.number + 1)
    text = "סיימת את השלב! עובר לשלב %d" % state.level.number
    if exit_mission:
        text += " | השלמת את המשימה!"
    state.say(text)


def _place_player(state: GameState) -> None:
    player = state.player
    player.x, player.y = tile_center(*START_TILE)
    player.dir = (0.0, 1.0)
    player.invuln = SPAWN_INVULN_FRAMES
