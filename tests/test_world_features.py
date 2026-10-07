# -*- coding: utf-8 -*-
"""בדיקות לשערים ומפתחות, קירות משוריינים ולבני חבלה, ומשימות."""

import random

import pytest

from dungeons_and_guns.config import TILE
from dungeons_and_guns.data import CATALOG
from dungeons_and_guns.models import (ItemKind, Mission, MissionKind, SlotItem, Tile, WeaponKind,
                                      WheelOutcome)
from dungeons_and_guns.systems import (combat, crafting, enemies, interaction, missions,
                                       progression, shop, simulation, weather)
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


# ---------- ערפל ----------
def test_fog_comes_and_goes(state):
    weather.update(state)                               # קובע מתי הערפל הראשון
    w = state.weather
    assert w.next_fog_at > state.now and not weather.foggy(state)
    state.now = w.next_fog_at
    weather.update(state)
    assert weather.foggy(state) and "ערפל" in state.feedback.message
    assert w.next_fog_at > w.fog_until                  # הערפל הבא רק אחרי שזה נגמר
    state.now = w.fog_until
    weather.update(state)
    assert not weather.foggy(state) and "התפזר" in state.feedback.message


def test_fog_fades_in(state):
    state.weather.fog_start, state.weather.fog_until = state.now, state.now + 60_000
    assert weather.fog_strength(state) == 0
    state.now += weather.FADE_MS // 2
    assert 0 < weather.fog_strength(state) < 1
    state.now += weather.FADE_MS
    assert weather.fog_strength(state) == 1


def put_enemy(state, distance):
    enemy = make_enemy(state.level, state.player.x + distance, state.player.y)
    enemy.weapon = CATALOG.weapon("barrett82")          # טווח ארוך - יורה גם מרחוק
    state.level.enemies.append(enemy)
    return enemy


def test_enemy_far_away_in_fog_does_not_see_you(state):
    enemy = put_enemy(state, 250)
    state.weather.fog_start, state.weather.fog_until = state.now, state.now + 60_000
    x = enemy.x
    enemies.update_enemies(state)
    assert not state.level.bullets and enemy.x == x


def test_enemy_close_in_fog_still_shoots(state):
    put_enemy(state, 80)
    state.weather.fog_start, state.weather.fog_until = state.now, state.now + 60_000
    enemies.update_enemies(state)
    assert state.level.bullets


def test_without_fog_far_enemy_shoots(state):
    put_enemy(state, 250)
    enemies.update_enemies(state)
    assert state.level.bullets


# ---------- ציוד ורימונים של אויבים ----------
def test_enemies_get_gear_and_grenades_more_in_later_levels():
    random.seed(9)
    early, late = build_level(1), build_level(10)

    def equipped(level):
        return [make_enemy(level, 50, 50) for _ in range(300)]
    early_gear = sum(len(e.gear) + len(e.grenades) for e in equipped(early))
    late_enemies = equipped(late)
    late_gear = sum(len(e.gear) + len(e.grenades) for e in late_enemies)
    assert 0 < early_gear < late_gear
    seen = {g for e in late_enemies for g in e.gear} | {g for e in late_enemies for g in e.grenades}
    assert {"helmet", "vest", "shield", "laser", "sight", "grenade", "smoke"} <= seen


def bare_enemy(state, distance=100, **kw):
    enemy = make_enemy(state.level, state.player.x + distance, state.player.y)
    enemy.gear, enemy.grenades = [], {}
    for key, value in kw.items():
        setattr(enemy, key, value)
    state.level.enemies.append(enemy)
    return enemy


def test_enemy_helmet_and_vest_take_less_damage(state):
    plain = bare_enemy(state)
    armored = bare_enemy(state, gear=["helmet", "vest"])
    combat.damage_enemy(state, plain, 10)
    combat.damage_enemy(state, armored, 10)
    assert armored.max_hp - armored.hp < plain.max_hp - plain.hp


def test_enemy_laser_makes_bullets_more_accurate(state):
    plain = bare_enemy(state, distance=80)
    enemies.update_enemies(state)
    plain_acc = state.level.bullets[-1].acc
    state.level.enemies.clear()
    state.level.bullets.clear()
    bare_enemy(state, distance=80, gear=["laser"])
    enemies.update_enemies(state)
    assert state.level.bullets[-1].acc > plain_acc


def test_enemy_throws_grenade_that_hurts_only_you(state, monkeypatch):
    monkeypatch.setattr(enemies.random, "random", lambda: 0.0)
    open_room(state)                                      # בלי קירות שהרימון יקפוץ מהם
    thrower = bare_enemy(state, distance=90, grenades={"grenade": 1})
    friend = bare_enemy(state, distance=30)               # קרוב לפיצוץ - אבל לא נפגע
    state.player.invuln = 0
    enemies.update_enemies(state)
    assert len(state.level.grenades) == 1 and state.level.grenades[0].from_enemy
    assert thrower.grenades["grenade"] == 0
    for _ in range(200):                                  # הרימון עף ומתפוצץ
        state.now += 16
        combat.update_grenades(state)
    assert not state.level.grenades
    assert state.player.hp < state.player.max_hp
    assert friend.hp == friend.max_hp


def test_wounded_enemy_hides_in_smoke(state):
    enemy = bare_enemy(state, distance=200, grenades={"smoke": 1})
    enemy.hp = enemy.max_hp * 0.3
    enemies.update_enemies(state)
    assert enemy.grenades["smoke"] == 0
    state.now += 1000
    combat.update_grenades(state)
    assert combat.in_smoke_at(state, enemy.x, enemy.y)


def test_harder_to_hit_enemy_in_smoke(state, monkeypatch):
    monkeypatch.setattr(combat.random, "random", lambda: 0.6)   # פוגע רק בדיוק מעל 60%
    enemy = bare_enemy(state, distance=40)
    from dungeons_and_guns.models import Bullet, SmokeCloud
    state.level.smokes.append(SmokeCloud(x=enemy.x, y=enemy.y, r=80, until=state.now + 9000))
    state.level.bullets.append(Bullet(x=enemy.x - 20, y=enemy.y, dx=1, dy=0, speed=10,
                                      dmg=(10, 10), acc=0.9, rng=300, from_player=True))
    combat.update_bullets(state)
    combat.update_bullets(state)
    assert enemy.hp == enemy.max_hp                       # 0.9 * 0.5 = 0.45 < 0.6 - החטיא


@pytest.mark.parametrize("roll, looted", [(0.3, True), (0.6, False)])
def test_enemy_grenades_are_loot_only_sometimes(state, monkeypatch, roll, looted):
    monkeypatch.setattr(combat.random, "random", lambda: roll)
    enemy = bare_enemy(state, grenades={"grenade": 2, "smoke": 1})
    combat.damage_enemy(state, enemy, 10_000)
    assert state.inventory.throwable_count("grenade") == (2 if looted else 0)
    assert state.inventory.throwable_count("smoke") == (1 if looted else 0)


# ---------- קירות עוצרים חרב ולייזר ----------
def test_sword_does_not_hit_through_wall(state):
    open_room(state)
    level = state.level
    from dungeons_and_guns.systems.inventory import give_weapon
    give_weapon(state.inventory, CATALOG.weapon("sword"))
    state.inventory.select_slot(state.inventory.hotbar_index(SlotItem(kind=ItemKind.WEAPON, id="sword")))
    state.player.dir = (1.0, 0.0)
    behind_wall = bare_enemy(state, distance=40)
    level.grid[2][3] = Tile.WALL                        # קיר בין השחקן (2,2) לאויב
    simulation.use_selected(state)
    assert behind_wall.hp == behind_wall.max_hp
    level.grid[2][3] = Tile.FLOOR                       # בלי הקיר - פוגע
    state.now += 5000
    simulation.use_selected(state)
    assert behind_wall.hp < behind_wall.max_hp


def test_ray_stops_at_wall(state):
    open_room(state)
    level = state.level
    x, y = state.player.x, state.player.y               # באמצע משבצת (2,2)
    assert level.ray_length(x, y, 1, 0, 500) < 3 * TILE + TILE      # נעצר בקיר של החדר
    level.grid[2][3] = Tile.ARMORED
    assert level.ray_length(x, y, 1, 0, 500) < TILE
    assert not level.clear_line(x, y, x + 2 * TILE, y)
    assert level.clear_line(x, y, x, y + TILE)
