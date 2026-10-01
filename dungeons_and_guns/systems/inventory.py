# -*- coding: utf-8 -*-
"""מה יש לשחקן, ואיך הציוד משפיע עליו."""

import random

from ..data import CATALOG
from ..models import Gear, GameState, Inventory, ItemBase, ItemKind, SlotItem, Tool, Weapon


def current_weapon(state: GameState) -> Weapon | None:
    """הנשק שבמשבצת הנבחרת בשורת המספרים (None אם נבחרה תרופה, אוכל או משבצת ריקה)."""
    item = state.inventory.selected_item
    if item is None or item.kind != ItemKind.WEAPON:
        return None
    return CATALOG.weapon(item.id)


def gear_items(ids) -> list[Gear]:
    """פריטי הציוד לפי ה-id שלהם (של השחקן או של אויב)."""
    return [g for g in CATALOG.gear if g.id in ids]


def owned_gear(inv: Inventory) -> list[Gear]:
    return gear_items(inv.gear)


def reduce_multiplier(gear: list[Gear]) -> float:
    """כמה נזק באמת נכנס אחרי המגן, השכפ"ץ והקסדה."""
    mult = 1.0
    for item in gear:
        if item.reduce:
            mult *= 1.0 - item.reduce
    return mult


def give_weapon(inv: Inventory, weapon: Weapon) -> None:
    """נותן נשק חדש, ואיתו חפיסת תחמושת אחת כדי שאפשר יהיה לירות בו."""
    if weapon.id not in inv.weapons:
        inv.weapons.append(weapon.id)
    inv.add_to_hotbar(SlotItem(kind=ItemKind.WEAPON, id=weapon.id))
    ammo = CATALOG.ammo_for(weapon)
    if ammo:
        inv.add_ammo(ammo.id, ammo.pack)


def owns(inv: Inventory, kind: ItemKind, item_id: str) -> bool:
    """פריטים שמקבלים פעם אחת בלבד (כלי, נשק, ציוד) - האם כבר יש אותו."""
    match kind:
        case ItemKind.TOOL:
            return item_id in inv.tools
        case ItemKind.WEAPON:
            return item_id in inv.weapons
        case ItemKind.GEAR:
            return item_id in inv.gear
        case _:
            return False


def give_item(inv: Inventory, kind: ItemKind, item: ItemBase) -> None:
    """נותן פריט אחד מהקטלוג (חפיסת תחמושת שלמה, רימון אחד, תרופה אחת...)."""
    match kind:
        case ItemKind.TOOL:
            inv.tools.add(item.id)
        case ItemKind.GEAR:
            inv.gear.add(item.id)
        case ItemKind.WEAPON:
            give_weapon(inv, item)
        case ItemKind.AMMO:
            inv.add_ammo(item.id, item.pack)
        case ItemKind.THROWABLE:
            inv.add_throwable(item.id, 1)
        case ItemKind.POTION:
            inv.add_potion(item.id)
        case ItemKind.FOOD:
            inv.add_food(item.id)
        case ItemKind.KEY:
            inv.keys += 1
        case ItemKind.OVEN:
            inv.oven_uses += item.uses
        case ItemKind.POISON:
            inv.poison_arrows += item.arrows


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
    return reduce_multiplier(owned_gear(inv))


def aim_bonus(inv: Inventory) -> tuple[float, float]:
    gear = owned_gear(inv)
    return sum(g.acc for g in gear), sum(g.rng for g in gear)


def move_speed(inv: Inventory) -> float:
    slow = sum(g.slow for g in owned_gear(inv))
    return 2.6 * max(0.5, 1.0 - slow)
