# -*- coding: utf-8 -*-
"""מה יש לשחקן, ואיך הציוד משפיע עליו."""

import random

from ..data import CATALOG
from ..models import Gear, GameState, Inventory, Tool, Weapon


def current_weapon(state: GameState) -> Weapon:
    return CATALOG.weapon(state.inventory.weapon_id)


def owned_gear(inv: Inventory) -> list[Gear]:
    return [g for g in CATALOG.gear if g.id in inv.gear]


def give_weapon(inv: Inventory, weapon: Weapon) -> None:
    """נותן נשק חדש, ואיתו חפיסת תחמושת אחת כדי שאפשר יהיה לירות בו."""
    if weapon.id not in inv.weapons:
        inv.weapons.append(weapon.id)
    ammo = CATALOG.ammo_for(weapon)
    if ammo:
        inv.add_ammo(ammo.id, ammo.pack)


def give_random_tool(inv: Inventory) -> Tool | None:
    options = [t for t in CATALOG.tools if t.id not in inv.tools]
    if not options:
        return None
    tool = random.choice(options)
    inv.tools.add(tool.id)
    return tool


def give_random_gear(inv: Inventory) -> Gear | None:
    options = [g for g in CATALOG.gear if g.id not in inv.gear]
    if not options:
        return None
    item = random.choice(options)
    inv.gear.add(item.id)
    return item


def damage_multiplier(inv: Inventory) -> float:
    """כמה נזק באמת נכנס אחרי המגן, השכפ"ץ והקסדה."""
    mult = 1.0
    for item in owned_gear(inv):
        if item.reduce:
            mult *= 1.0 - item.reduce
    return mult


def aim_bonus(inv: Inventory) -> tuple[float, float]:
    gear = owned_gear(inv)
    return sum(g.acc for g in gear), sum(g.rng for g in gear)


def move_speed(inv: Inventory) -> float:
    slow = sum(g.slow for g in owned_gear(inv))
    return 2.6 * max(0.5, 1.0 - slow)
