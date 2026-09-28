# -*- coding: utf-8 -*-
"""הסדנה: מכינים תחמושת וציוד מהחומרים שבתיק."""

from ..data import CATALOG
from ..models import GameState, Recipe, ResourceKind
from .inventory import give_item, owns


def missing(state: GameState, recipe: Recipe) -> dict[ResourceKind, int]:
    """כמה חסר מכל חומר (ריק = אפשר להכין)."""
    inv = state.inventory
    return {kind: need - inv.material_count(kind) for kind, need in recipe.needs.items()
            if inv.material_count(kind) < need}


def already_made(state: GameState, recipe: Recipe) -> bool:
    return owns(state.inventory, recipe.kind, recipe.item)


def craft(state: GameState, recipe: Recipe) -> bool:
    """מכין את הפריט אם יש מספיק חומרים. מחזיר True אם ההכנה הצליחה."""
    if already_made(state, recipe):
        return False
    item = CATALOG.item(recipe.kind, recipe.item)
    lacking = missing(state, recipe)
    if lacking:
        state.play("no", gap=400)
        state.say("חסר לך: %s" % ", ".join(
            "%d %s" % (n, CATALOG.resource(kind).material) for kind, n in lacking.items()))
        return False
    inv = state.inventory
    for kind, need in recipe.needs.items():
        inv.materials[kind] -= need
        if not inv.materials[kind]:
            del inv.materials[kind]
    give_item(inv, recipe.kind, item)
    state.play("buy")
    state.say("הכנת %s!" % item.name)
    return True
