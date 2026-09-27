# -*- coding: utf-8 -*-
"""בדיקות לחוקי המשחק - רצות בלי חלון ובלי pygame."""

import random
import subprocess
import sys

import pytest
from pydantic import ValidationError

from dungeons_and_guns.data import CATALOG, Catalog
from dungeons_and_guns.models import (Crate, CrateKind, PlayerInput, Tile, Weapon,
                                      WeaponCategory, WeaponKind, WheelOutcome)
from dungeons_and_guns.systems import combat, crates, health, progression, shop, simulation
from dungeons_and_guns.systems import wheel as wheel_system
from dungeons_and_guns.systems.shop import ShopKind, ShopRow
from dungeons_and_guns.world import START_TILE, build_level, make_enemy, path_exists


@pytest.fixture
def state():
    random.seed(1234)
    s = progression.new_game()
    s.level.enemies.clear()             # שקט - בלי אויבים שיורים בנו
    s.now = 10_000
    return s


def test_logic_does_not_import_pygame():
    code = ("import sys; import dungeons_and_guns.systems.simulation, dungeons_and_guns.systems.shop; "
            "sys.exit('pygame' in sys.modules)")
    assert subprocess.run([sys.executable, "-c", code]).returncode == 0


# ---------- קטלוג ----------
def test_catalog_ammo_defaults_follow_category():
    assert CATALOG.weapon("m16").ammo == "ammo_rifle"
    assert CATALOG.weapon("ak47").ammo == "ammo_ak"
    assert CATALOG.weapon("ruger101").ammo == "ammo_revolver"
    assert CATALOG.weapon("bow").ammo == "ammo_arrow"
    assert CATALOG.weapon("slingshot").ammo is None
    assert CATALOG.weapon("dagger").ammo is None


def test_enemy_weapons_are_sorted_guns_only():
    prices = [w.price for w in CATALOG.enemy_weapons]
    assert prices == sorted(prices)
    assert all(w.kind == WeaponKind.GUN and w.cat != WeaponCategory.COLD
               for w in CATALOG.enemy_weapons)


def test_weapon_rejects_bad_damage_range():
    with pytest.raises(ValidationError):
        Weapon(id="x", name="x", cat=WeaponCategory.PISTOLS, kind=WeaponKind.GUN,
               dmg=(10, 5), acc=0.5, rng=100, cooldown=100, price=1)


def test_catalog_rejects_unknown_ammo():
    bad = CATALOG.weapons + [Weapon(id="x", name="x", cat=WeaponCategory.PISTOLS,
                                    kind=WeaponKind.GUN, dmg=(1, 2), acc=0.5, rng=100,
                                    cooldown=100, price=1, ammo="nope")]
    fields = {name: getattr(CATALOG, name) for name in Catalog.model_fields}
    with pytest.raises(ValidationError, match="unknown ammo"):
        Catalog(**{**fields, "weapons": bad})


# ---------- עולם ----------
@pytest.mark.parametrize("number", [1, 3, 6])
def test_level_always_has_dry_path_to_exit(number):
    random.seed(number)
    level = build_level(number)
    assert path_exists(level.grid, START_TILE, level.exit_tile)
    assert any(t == Tile.FISH for row in level.grid for t in row)


# ---------- ירי ----------
def test_shooting_uses_ammo_and_respects_cooldown(state):
    before = state.inventory.ammo_count("ammo_pistol")
    combat.player_shoot(state)
    combat.player_shoot(state)              # עדיין בזמן ההמתנה של הנשק
    assert state.inventory.ammo_count("ammo_pistol") == before - 1
    assert len(state.level.bullets) == 1


def test_shooting_without_ammo_says_so(state):
    state.inventory.ammo["ammo_pistol"] = 0
    combat.player_shoot(state)
    assert not state.level.bullets
    assert "נגמרו" in state.feedback.message
    assert any(c.name == "no" for c in state.feedback.sounds)


def test_killing_enemy_pays_money(state):
    enemy = make_enemy(state.level, 100, 100)
    state.level.enemies.append(enemy)
    money = state.inventory.money
    combat.damage_enemy(state, enemy, 10_000)
    assert enemy not in state.level.enemies
    assert state.inventory.money > money


def test_twin_enemies_are_distinct(state):
    a = make_enemy(state.level, 50, 50)
    b = a.model_copy(update={"uid": a.uid + 10_000})
    state.level.enemies += [a, b]
    state.level.enemies.remove(b)
    assert state.level.enemies == [a]


# ---------- חיים ----------
def test_gear_reduces_damage(state):
    state.inventory.gear.add("vest")
    health.hurt(state, 10)
    assert state.player.hp == pytest.approx(93)


def test_death_plays_gameover_once(state):
    health.hurt(state, 1000)
    health.drain(state, 5)
    assert state.game_over
    assert [c.name for c in state.feedback.sounds].count("gameover") == 1


def test_only_large_potion_cures_sickness(state):
    health.infect(state)
    state.player.hp = 50
    state.inventory.add_potion("small")
    health.drink_potion(state)
    assert state.player.sick and state.player.hp == 50
    state.now += 1000
    state.inventory.add_potion("large")
    health.drink_potion(state)
    assert not state.player.sick and state.player.hp == 100


# ---------- חנות ----------
def test_buying_weapon_gives_ammo_pack(state):
    state.inventory.money = 5000
    m16 = CATALOG.weapon("m16")
    assert shop.buy(state, ShopRow(kind=ShopKind.WEAPON, item=m16))
    assert "m16" in state.inventory.weapons
    assert state.inventory.ammo_count("ammo_rifle") == CATALOG.ammo("ammo_rifle").pack
    assert state.inventory.money == 5000 - m16.price


def test_cannot_buy_without_money(state):
    state.inventory.money = 0
    assert not shop.buy(state, ShopRow(kind=ShopKind.TOOL, item=CATALOG.tool("saw")))
    assert "saw" not in state.inventory.tools


def test_shop_marks_owned_items(state):
    rows = [r for s in shop.shop_sections(state) for r in s.rows]
    glock = next(r for r in rows if r.item.id == "glock19")
    assert glock.owned


# ---------- תיבות וגלגל ----------
def test_empty_crate_is_removed(state):
    crate = Crate(x=0, y=0, kind=CrateKind.EMPTY)
    state.level.crates.append(crate)
    crates.open_crate(state, crate)
    assert crate not in state.level.crates
    assert "ריקה" in state.feedback.message


def test_wheel_spins_down_and_pays_out(state):
    state.inventory.money = 1000
    wheel_system.spin(state)
    for _ in range(2000):
        wheel_system.update(state)
        if state.wheel.done:
            break
    assert state.wheel.done and state.wheel.text
    wheel_system.close(state)
    assert state.wheel is None


def test_wheel_heal_outcome(state):
    state.player.hp = 5
    slice_ = next(s for s in CATALOG.wheel_slices if s.id == WheelOutcome.HEAL)
    wheel_system.apply(state, slice_)
    assert state.player.hp == state.player.max_hp


# ---------- סימולציה ----------
def test_simulation_runs_many_frames(state):
    random.seed(7)
    state = progression.new_game()
    for frame in range(600):
        state.now = frame * 16
        simulation.step(state, PlayerInput(dx=1, dy=1, shoot=True, interact=True))
        if state.game_over:
            break
    assert state.player.x > 0


def test_paused_while_shop_open(state):
    x = state.player.x
    simulation.step(state, PlayerInput(dx=1), shop_open=True)
    assert state.player.x == x
