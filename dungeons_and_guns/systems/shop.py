# -*- coding: utf-8 -*-
"""מה יש בחנות ומה קורה כשקונים."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from ..data import CATALOG
from ..models import GameState, ItemBase
from . import wheel
from .inventory import give_weapon


class ShopKind(StrEnum):
    TOOL = "tool"
    WEAPON = "weapon"
    THROWABLE = "throwable"     # רימונים - נקנים ביחידות
    AMMO = "ammo"
    WHEEL = "wheel"
    GEAR = "gear"
    POTION = "potion"


class ShopRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: ShopKind
    item: ItemBase
    owned: bool = False         # פריט שקונים פעם אחת וכבר נקנה


class ShopSection(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str
    rows: list[ShopRow]


def shop_sections(state: GameState) -> list[ShopSection]:
    inv = state.inventory
    sections = [ShopSection(title="כלים", rows=[
        ShopRow(kind=ShopKind.TOOL, item=t, owned=t.id in inv.tools) for t in CATALOG.tools])]
    for cat in CATALOG.weapon_categories:
        rows = []
        for w in CATALOG.weapons:
            if w.cat != cat:
                continue
            if w.is_throwable:
                rows.append(ShopRow(kind=ShopKind.THROWABLE, item=w))
            else:
                rows.append(ShopRow(kind=ShopKind.WEAPON, item=w, owned=w.id in inv.weapons))
        sections.append(ShopSection(title=cat, rows=rows))
    sections.append(ShopSection(title="תחמושת", rows=[
        ShopRow(kind=ShopKind.AMMO, item=a) for a in CATALOG.ammo_types]))
    sections.append(ShopSection(title="גלגל המזל", rows=[
        ShopRow(kind=ShopKind.WHEEL, item=CATALOG.wheel_ticket)]))
    for cat in CATALOG.gear_categories:
        sections.append(ShopSection(title=cat, rows=[
            ShopRow(kind=ShopKind.GEAR, item=g, owned=g.id in inv.gear)
            for g in CATALOG.gear if g.cat == cat]))
    sections.append(ShopSection(title="תרופות", rows=[
        ShopRow(kind=ShopKind.POTION, item=p) for p in CATALOG.potions]))
    return sections


def buy(state: GameState, row: ShopRow) -> bool:
    """קונה את הפריט אם יש מספיק כסף. מחזיר True אם הקנייה הצליחה."""
    inv, item = state.inventory, row.item
    if row.owned or inv.money < item.price:
        return False
    inv.money -= item.price
    state.play("buy")

    match row.kind:
        case ShopKind.TOOL:
            inv.tools.add(item.id)
            state.say("קנית %s!" % item.name)
        case ShopKind.GEAR:
            inv.gear.add(item.id)
            state.say("קנית %s!" % item.name)
        case ShopKind.WEAPON:
            give_weapon(inv, item)
            ammo = CATALOG.ammo_for(item)
            if ammo:
                state.say("קנית %s! קיבלת גם %d %s" % (item.name, ammo.pack, ammo.name))
            else:
                state.say("קנית %s!" % item.name)
        case ShopKind.AMMO:
            inv.add_ammo(item.id, item.pack)
            state.say("קנית %d %s!" % (item.pack, item.name))
        case ShopKind.THROWABLE:
            inv.add_throwable(item.id, 1)
            state.say("קנית %s!" % item.name)
        case ShopKind.POTION:
            inv.add_potion(item.id)
            state.say("קנית %s!" % item.name)
        case ShopKind.WHEEL:
            wheel.spin(state)
    return True
