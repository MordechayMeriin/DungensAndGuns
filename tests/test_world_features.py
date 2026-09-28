# -*- coding: utf-8 -*-
"""בדיקות לשערים ומפתחות, קירות משוריינים ולבני חבלה, ומשימות."""

import random

import pytest

from dungeons_and_guns.config import TILE
from dungeons_and_guns.data import CATALOG
from dungeons_and_guns.models import (ItemKind, Mission, MissionKind, SlotItem, Tile, WeaponKind,
                                      WheelOutcome)
from dungeons_and_guns.systems import (combat, crafting, interaction, missions, progression, shop,
                                       simulation)
from dungeons_and_guns.systems import wheel as wheel_system
from dungeons_and_guns.systems.shop import ShopKind, ShopRow
from dungeons_and_guns.world import START_TILE, build_level, make_enemy, path_exists


@pytest.fixture
def state():
    random.seed(4321)
    s = progression.new_game()
    s.level.enemies.clear()
    s.mission = None
    s.now = 10_000
    return s


def open_room(state):
    """מבוך קטן ומוכר: חדר 5x5 של רצפה מוקף קירות, השחקן באמצע (2,2)."""
    level = state.level
    for y in range(level.rows):
        for x in range(level.cols):
            level.grid[y][x] = Tile.WALL
    for y in range(1, 6):
        for x in range(1, 6):
            level.grid[y][x] = Tile.FLOOR
    level.resources.clear()
    level.crates.clear()
    level.exit_tile = (level.cols - 2, level.rows - 2)
    state.player.x, state.player.y = 2 * TILE + TILE / 2, 2 * TILE + TILE / 2


# ---------- שערים ומפתחות ----------
def test_gate_blocks_walking_and_bullets(state):
    open_room(state)
    level = state.level
    level.grid[2][3] = Tile.GATE
    assert level.is_wall(3 * TILE + 5, 2 * TILE + 5)
    assert not level.can_move(3 * TILE + 5, 2 * TILE + TILE / 2, state.player.r)


def test_key_opens_gate_and_is_used_up(state):
    open_room(state)
    state.level.grid[2][3] = Tile.GATE
    state.inventory.keys = 1
    interaction.interact(state)
    assert state.level.grid[2][3] == Tile.FLOOR
    assert state.inventory.keys == 0


def test_gate_without_key_stays_closed(state):
    open_room(state)
    state.level.grid[2][3] = Tile.GATE
    interaction.interact(state)
    assert state.level.grid[2][3] == Tile.GATE
    assert "מפתח" in state.feedback.message
    assert "מפתח" in interaction.interact_hint(state)


def test_buy_and_craft_keys(state):
    state.inventory.money = 100
    assert shop.buy(state, ShopRow(kind=ShopKind.KEY, item=CATALOG.key))
    assert state.inventory.keys == 1 and state.inventory.money == 100 - 20
    recipe = next(r for r in CATALOG.recipes if r.kind == ItemKind.KEY)
    for kind, n in recipe.needs.items():
        state.inventory.add_material(kind, n)
    assert crafting.craft(state, recipe)
    assert state.inventory.keys == 2


def test_wheel_can_give_keys(state):
    slice_ = next(s for s in CATALOG.wheel_slices if s.id == WheelOutcome.KEYS)
    wheel_system.apply(state, slice_)
    assert state.inventory.keys == 2


# ---------- קירות ולבני חבלה ----------
def blow_up(state, weapon_id):
    """מניח לבנה במקום של השחקן, מתרחק, ומחכה לפיצוץ."""
    inv = state.inventory
    inv.add_throwable(weapon_id, 1)
    inv.select_slot(inv.hotbar_index(SlotItem(kind=ItemKind.WEAPON, id=weapon_id)))
    simulation.use_selected(state)
    assert len(state.level.grenades) == 1
    state.player.x += 10 * TILE                         # ברחנו
    state.now += 3500
    combat.update_grenades(state)
    assert not state.level.grenades


def test_tnt_breaks_regular_wall_but_not_armored(state):
    open_room(state)
    grid = state.level.grid
    grid[2][2] = Tile.FLOOR
    grid[1][2] = Tile.WALL                              # מעל
    grid[3][2] = Tile.ARMORED                           # מתחת
    blow_up(state, "tnt")
    assert grid[1][2] == Tile.FLOOR
    assert grid[3][2] == Tile.ARMORED


def test_semtex_breaks_armored_wall(state):
    open_room(state)
    grid = state.level.grid
    grid[3][2] = Tile.ARMORED
    blow_up(state, "semtex")
    assert grid[3][2] == Tile.FLOOR


def test_outer_wall_never_breaks(state):
    open_room(state)
    state.player.x, state.player.y = 1 * TILE + TILE / 2, 1 * TILE + TILE / 2
    blow_up(state, "semtex")
    assert state.level.grid[0][1] == Tile.WALL and state.level.grid[1][0] == Tile.WALL


def test_charge_hurts_player_who_does_not_run(state):
    open_room(state)
    state.player.invuln = 0                             # בלי ההגנה של תחילת השלב
    state.inventory.add_throwable("tnt", 1)
    state.inventory.select_slot(state.inventory.hotbar_index(SlotItem(kind=ItemKind.WEAPON, id="tnt")))
    simulation.use_selected(state)
    state.now += 3500
    combat.update_grenades(state)
    assert state.player.hp < state.player.max_hp


def test_explosives_are_sold_and_placed():
    for wid in ("tnt", "semtex"):
        w = CATALOG.weapon(wid)
        assert w.kind == WeaponKind.PLACE and w.is_throwable and w.wall_power
    assert CATALOG.weapon("semtex").wall_power > CATALOG.weapon("tnt").wall_power


@pytest.mark.parametrize("number", [1, 3, 6])
def test_levels_have_gates_and_armored_walls_but_exit_is_open(number):
    random.seed(number)
    level = build_level(number)
    tiles = [t for row in level.grid for t in row]
    assert Tile.ARMORED in tiles
    assert Tile.GATE in tiles
    assert path_exists(level.grid, START_TILE, level.exit_tile)


# ---------- משימות ----------
def test_new_game_and_new_level_get_a_mission():
    random.seed(1)
    s = progression.new_game()
    assert s.mission is not None and s.mission.deadline > s.now
    s.mission = None
    progression.enter_level(s, 2)
    assert s.mission is not None


def test_mission_carries_over_to_next_level(state):
    state.mission = Mission(kind=MissionKind.KILL, goal=5, progress=2, deadline=state.now + 60_000,
                            money=100, points=10)
    progression.enter_level(state, 2)
    assert state.mission.progress == 2


def test_kill_mission_pays_when_done(state):
    state.mission = Mission(kind=MissionKind.KILL, goal=2, deadline=state.now + 60_000,
                            money=150, points=20)
    for _ in range(2):
        enemy = make_enemy(state.level, 100, 100)
        state.level.enemies.append(enemy)
        money, points = state.inventory.money, state.player.points
        combat.damage_enemy(state, enemy, 10_000)
    assert state.mission is None
    assert state.inventory.money > money + 150 - 1
    assert "המשימה" in state.feedback.message


def test_other_things_do_not_count(state):
    state.mission = Mission(kind=MissionKind.CRATES, goal=2, deadline=state.now + 60_000,
                            money=150, points=20)
    missions.progress(state, MissionKind.KILL)
    assert state.mission.progress == 0


def test_mission_fails_when_time_runs_out(state):
    state.mission = Mission(kind=MissionKind.HARVEST, goal=3, deadline=state.now + 1000,
                            money=150, points=20)
    money = state.inventory.money
    state.now += 2000
    missions.update(state)
    assert state.mission is None
    assert state.inventory.money == money
    assert "נכשלה" in state.feedback.message


def test_exit_mission_done_by_leaving_level(state):
    state.mission = Mission(kind=MissionKind.EXIT, goal=1, deadline=state.now + 60_000,
                            money=200, points=30)
    money = state.inventory.money
    progression.leave_level(state)
    assert state.inventory.money == money + 200
    assert state.level.number == 2
    assert state.mission is not None and state.mission.progress == 0     # משימה חדשה לשלב 2
