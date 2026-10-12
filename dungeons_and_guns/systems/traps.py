# -*- coding: utf-8 -*-
"""מלכודת נסתרת: מי שדורך עליה נתקע לכמה שניות, ומאבד כסף ואחד מהנשקים הכי טובים שלו."""

import random

from ..config import TILE
from ..data import CATALOG
from ..models import GameState
from . import particles

TRAP_STUCK_MS = 3000
TRAP_MONEY_SHARE = 0.3      # כמה מהכסף המלכודת לוקחת
TRAP_TOP_WEAPONS = 7        # המלכודת לוקחת אחד מ-7 הנשקים הכי טובים (יקרים) שלך


def check_trap(state: GameState) -> None:
    level, player = state.level, state.player
    if level.trap is None or (int(player.x // TILE), int(player.y // TILE)) != level.trap:
        return
    level.sprung_trap, level.trap = level.trap, None       # כל מלכודת עובדת פעם אחת
    player.stuck_until = state.now + TRAP_STUCK_MS
    inv = state.inventory
    lost = int(inv.money * TRAP_MONEY_SHARE)
    inv.money -= lost
    weapon = take_best_weapon(state)
    state.play("crate_bad")
    particles.burst(level, player.x, player.y, 16, 3, 24, ((150, 150, 160), (200, 60, 60)))
    lost_weapon = ""
    if weapon:                                      # "את ה-M16" אבל "את החרב"
        lost_weapon = " ואת ה%s%s" % ("-" if weapon[0].isascii() else "", weapon)
    state.say("נפלת למלכודת! איבדת %d כסף%s" % (lost, lost_weapon))


def take_best_weapon(state: GameState) -> str:
    """לוקח נשק אקראי מתוך 7 הכי יקרים - אבל אף פעם לא את הנשק האחרון (רימונים לא נחשבים)."""
    inv = state.inventory
    guns = [CATALOG.weapon(w) for w in inv.weapons if not CATALOG.weapon(w).is_throwable]
    if len(guns) < 2:
        return ""
    best = sorted(guns, key=lambda w: w.price, reverse=True)[:TRAP_TOP_WEAPONS]
    taken = random.choice(best)
    inv.weapons.remove(taken.id)
    for i, item in enumerate(inv.hotbar):
        if item is not None and item.id == taken.id:
            inv.clear_slot(i)
    return taken.name
