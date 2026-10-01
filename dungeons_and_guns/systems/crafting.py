# -*- coding: utf-8 -*-
"""הסדנה: מכינים תחמושת, ציוד, אוכל ותנור מהחומרים שבתיק, ומבשלים אוכל נא בתנור."""

from ..data import CATALOG
from ..models import Food, GameState, ItemKind, Recipe, ResourceKind, SlotItem
from .inventory import give_item, owns


def missing(state: GameState, recipe: Recipe) -> dict[ResourceKind, int]:
    """כמה חסר מכל חומר (ריק = אפשר להכין)."""
    inv = state.inventory
    return {kind: need - inv.material_count(kind) for kind, need in recipe.needs.items()
            if inv.material_count(kind) < need}


def missing_potions(state: GameState, recipe: Recipe) -> dict[str, int]:
    """כמה חסר מכל תרופה שהמתכון צריך."""
    inv = state.inventory
    return {pid: need - inv.potion_count(pid) for pid, need in recipe.potions.items()
            if inv.potion_count(pid) < need}


def can_craft(state: GameState, recipe: Recipe) -> bool:
    return not missing(state, recipe) and not missing_potions(state, recipe)


def already_made(state: GameState, recipe: Recipe) -> bool:
    return owns(state.inventory, recipe.kind, recipe.item)


def craft(state: GameState, recipe: Recipe) -> bool:
    """מכין את הפריט אם יש מספיק חומרים. מחזיר True אם ההכנה הצליחה."""
    if already_made(state, recipe):
        return False
    item = CATALOG.item(recipe.kind, recipe.item)
    if not can_craft(state, recipe):
        lacking = ["%d %s" % (n, CATALOG.resource(kind).material)
                   for kind, n in missing(state, recipe).items()]
        lacking += ["%d %s" % (n, CATALOG.potion(pid).name)
                    for pid, n in missing_potions(state, recipe).items()]
        state.play("no", gap=400)
        state.say("חסר לך: %s" % ", ".join(lacking))
        return False
    inv = state.inventory
    for kind, need in recipe.needs.items():
        inv.materials[kind] -= need
        if not inv.materials[kind]:
            del inv.materials[kind]
    for pid, need in recipe.potions.items():
        inv.potions[pid] -= need
    give_item(inv, recipe.kind, item)
    state.play("buy")
    if recipe.kind == ItemKind.OVEN:
        state.say("בנית תנור! אפשר לבשל בו %d פעמים (בסדנה)" % item.uses)
    elif recipe.kind == ItemKind.POISON:
        state.say("הכנת רעל! %d החיצים הבאים מורעלים" % inv.poison_arrows)
    else:
        state.say("הכנת %s!" % item.name)
    return True


def cook(state: GameState, raw: Food) -> bool:
    """מבשל מנה אחת של אוכל נא בתנור. כל בישול משתמש בתנור פעם אחת."""
    inv = state.inventory
    cooked = CATALOG.food(raw.cooks_into)
    if inv.oven_uses <= 0:
        state.play("no", gap=400)
        state.say("אין לך תנור - בנה אחד בסדנה מלבנים")
        return False
    if inv.food_count(raw.id) <= 0:
        state.play("no", gap=400)
        state.say("אין לך %s לבשל" % raw.name)
        return False
    inv.food[raw.id] -= 1
    if not inv.food[raw.id]:
        del inv.food[raw.id]
        slot = inv.hotbar_index(SlotItem(kind=ItemKind.FOOD, id=raw.id))
        cooked_item = SlotItem(kind=ItemKind.FOOD, id=cooked.id)
        if slot is not None and cooked_item not in inv.hotbar:
            inv.set_slot(slot, cooked_item)                      # המבושל נכנס למקום של הנא
    inv.add_food(cooked.id)
    inv.oven_uses -= 1
    state.play("potion")
    if inv.oven_uses:
        state.say("בישלת %s! (בתנור נשארו %d בישולים)" % (cooked.name, inv.oven_uses))
    else:
        state.say("בישלת %s! התנור נגמר - צריך לבנות חדש מלבנים" % cooked.name)
    return True
