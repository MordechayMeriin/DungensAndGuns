# -*- coding: utf-8 -*-
"""מה יש בחנות ומה קורה כשקונים (או מכינים בסדנה שבתוך החנות)."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from ..data import CATALOG
from ..models import Food, GameState, ItemBase, ItemKind, Rank, Recipe
from . import crafting, ranks, wheel
from .inventory import give_item


class ShopKind(StrEnum):
    # הערכים של סוגי הפריטים זהים ל-ItemKind, כך ש-ItemKind(row.kind) עובד
    TOOL = "tool"
    KEY = "key"
    WEAPON = "weapon"
    THROWABLE = "throwable"     # רימונים - נקנים ביחידות
    AMMO = "ammo"
    WHEEL = "wheel"
    GEAR = "gear"
    POTION = "potion"
    CRAFT = "craft"             # סדנה - משלמים בחומרים מהתיק ולא בכסף
    COOK = "cook"               # תנור - אוכל נא הופך למבושל
    POISON = "poison"           # רעל לחיצים


class ShopRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: ShopKind
    item: ItemBase
    owned: bool = False         # פריט שקונים פעם אחת וכבר נקנה
    recipe: Recipe | None = None    # רק בשורות של הסדנה
    need_rank: Rank | None = None   # נשק שעוד אין לך דרגה מספיק גבוהה בשבילו
    raw: Food | None = None         # רק בשורות של התנור: מה מבשלים


class ShopSection(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str
    rows: list[ShopRow]


def shop_sections(state: GameState) -> list[ShopSection]:
    inv = state.inventory
    sections = [ShopSection(title="סדנה - מכינים מהחומרים שאספת", rows=[
        ShopRow(kind=ShopKind.CRAFT, item=CATALOG.item(r.kind, r.item), recipe=r,
                owned=crafting.already_made(state, r)) for r in CATALOG.recipes])]
    sections.append(ShopSection(title="תנור - מבשלים אוכל נא", rows=[
        ShopRow(kind=ShopKind.COOK, item=CATALOG.food(f.cooks_into), raw=f)
        for f in CATALOG.raw_foods]))
    sections.append(ShopSection(title="כלים", rows=[
        ShopRow(kind=ShopKind.TOOL, item=t, owned=t.id in inv.tools) for t in CATALOG.tools]
        + [ShopRow(kind=ShopKind.KEY, item=CATALOG.key)]))
    for cat in CATALOG.weapon_categories:
        rows = []
        for w in CATALOG.weapons:
            if w.cat != cat:
                continue
            if w.is_throwable:
                rows.append(ShopRow(kind=ShopKind.THROWABLE, item=w))
            else:
                rows.append(ShopRow(kind=ShopKind.WEAPON, item=w, owned=w.id in inv.weapons,
                                    need_rank=ranks.rank_needed(state, w)))
        sections.append(ShopSection(title=cat, rows=rows))
    sections.append(ShopSection(title="תחמושת", rows=[
        ShopRow(kind=ShopKind.AMMO, item=a) for a in CATALOG.ammo_types]
        + [ShopRow(kind=ShopKind.POISON, item=CATALOG.poison)]))
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
    """קונה את הפריט אם יש מספיק כסף (או מכין אותו בסדנה). מחזיר True אם הצליח."""
    inv, item = state.inventory, row.item
    if row.kind == ShopKind.CRAFT:
        return crafting.craft(state, row.recipe)
    if row.kind == ShopKind.COOK:
        return crafting.cook(state, row.raw)
    if row.kind == ShopKind.WEAPON and (rank := ranks.rank_needed(state, item)) is not None:
        state.play("no", gap=400)
        state.say("צריך דרגת %s כדי לקנות %s (יש לך %d מתוך %d נקודות)"
                  % (rank.name, item.name, state.player.points, rank.points))
        return False
    if row.owned or inv.money < item.price:
        return False
    inv.money -= item.price
    state.play("buy")

    if row.kind == ShopKind.WHEEL:
        wheel.spin(state)
        return True
    give_item(inv, ItemKind(row.kind), item)
    ammo = CATALOG.ammo_for(item) if row.kind == ShopKind.WEAPON else None
    if ammo:
        state.say("קנית %s! קיבלת גם %d %s" % (item.name, ammo.pack, ammo.name))
    elif row.kind == ShopKind.AMMO:
        state.say("קנית %d %s!" % (item.pack, item.name))
    elif row.kind == ShopKind.POISON:
        state.say("קנית רעל! %d החיצים הבאים מורעלים" % inv.poison_arrows)
    else:
        state.say("קנית %s!" % item.name)
    return True
