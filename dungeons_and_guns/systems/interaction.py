# -*- coding: utf-8 -*-
"""מקש Q: מעבר שלב, איסוף משאבים, דיג ופתיחת תיבות."""

import math
import random

from ..config import TILE
from ..data import CATALOG
from ..models import Crate, GameState, Resource, ResourceKind, Tile
from ..world import make_enemy
from . import health
from .crates import open_crate
from .progression import leave_level

INTERACT_COOLDOWN_MS = 250
RESOURCE_REACH = 36
CRATE_REACH = 34
EXIT_REACH = 24
FISH_COOLDOWN_MS = 9000


# ---------- מה נמצא ליד השחקן ----------
def at_exit(state: GameState) -> bool:
    ex = state.level.exit_tile[0] * TILE + TILE / 2
    ey = state.level.exit_tile[1] * TILE + TILE / 2
    return math.hypot(state.player.x - ex, state.player.y - ey) < EXIT_REACH


def nearest_resource(state: GameState) -> Resource | None:
    best, best_d = None, RESOURCE_REACH
    for res in state.level.resources:
        d = math.hypot(res.x - state.player.x, res.y - state.player.y)
        if d < best_d:
            best, best_d = res, d
    return best


def nearest_fish_tile(state: GameState) -> tuple[int, int] | None:
    """מחפש אריח מים עם דגים ליד השחקן (אפשר לדוג גם מהחוף)."""
    level, player = state.level, state.player
    gx, gy = int(player.x // TILE), int(player.y // TILE)
    best, best_d = None, 1.7
    for ty in range(gy - 1, gy + 2):
        for tx in range(gx - 1, gx + 2):
            if 0 <= tx < level.cols and 0 <= ty < level.rows and level.grid[ty][tx] == Tile.FISH:
                d = math.hypot(tx + 0.5 - player.x / TILE, ty + 0.5 - player.y / TILE)
                if d < best_d:
                    best, best_d = (tx, ty), d
    return best


def nearby_crate(state: GameState) -> Crate | None:
    return next((c for c in state.level.crates
                 if math.hypot(c.x - state.player.x, c.y - state.player.y) < CRATE_REACH), None)


# ---------- Q ----------
def interact(state: GameState) -> None:
    if state.now - state.player.last_interact < INTERACT_COOLDOWN_MS:
        return
    if at_exit(state):
        leave_level(state)
    elif (res := nearest_resource(state)) is not None:
        harvest(state, res)
    elif (tile := nearest_fish_tile(state)) is not None:
        go_fishing(state, tile)
    elif (crate := nearby_crate(state)) is not None:
        open_crate(state, crate)
    else:
        return
    state.player.last_interact = state.now


def harvest(state: GameState, res: Resource) -> None:
    info = CATALOG.resource(res.kind)
    inv, level = state.inventory, state.level
    if info.tool and info.tool not in inv.tools:
        state.play("no", gap=400)
        state.say("צריך %s בשביל %s - קנה בחנות!" % (CATALOG.tool(info.tool).name, info.name))
        return
    if res.ready_at > state.now:
        state.play("no", gap=400)
        state.say("%s עוד לא מוכן - חכה קצת" % info.name)
        return

    gain = random.randint(*info.value)
    inv.money += gain
    state.play("pickup")

    if res.kind == ResourceKind.CAVE:
        extra = ""
        if random.random() < 0.4:
            inv.add_potion(random.choice(["small", "medium", "large"]))
            extra = " ומצאת תרופה"
        state.say("חקרת את המערה! +%d כסף%s" % (gain, extra))
        if random.random() < 0.35:
            level.enemies.append(make_enemy(level, res.x, res.y))
            state.say("יצא אויב מהמערה! היזהר")
    elif res.kind == ResourceKind.VOLCANO:
        if random.random() < 0.3:
            health.drain(state, 10)
            state.say("כרית בהר הגעש! +%d כסף אבל נכווית (-10 חיים)" % gain)
        else:
            state.say("כרית אבן געש! +%d כסף" % gain)
    elif res.kind == ResourceKind.COW and not state.player.sick and random.random() < 0.2:
        health.infect(state)
        state.say("נדבקת ממחלה מהפרה! רק תרופה גדולה תרפא אותך")
    else:
        state.say("אספת %s! +%d כסף" % (info.name, gain))

    if info.renew:
        res.ready_at = state.now + info.renew
    else:
        level.resources.remove(res)


def go_fishing(state: GameState, tile: tuple[int, int]) -> None:
    level = state.level
    if "rod" not in state.inventory.tools:
        state.play("no", gap=400)
        state.say("צריך חכה כדי לדוג - קנה בחנות!")
        return
    if level.fish_cooldown.get(tile, 0) > state.now:
        state.play("no", gap=400)
        state.say("אין כאן דגים כרגע - חכה קצת")
        return
    state.play("splash")
    gain = random.randint(9, 16)
    state.inventory.money += gain
    level.fish_cooldown[tile] = state.now + FISH_COOLDOWN_MS
    state.say("דגת דג! +%d כסף" % gain)


def interact_hint(state: GameState) -> str:
    """שורת עזרה קטנה שמראה מה אפשר לעשות במקום שבו אתה עומד."""
    inv = state.inventory
    if at_exit(state):
        return "Q = מעבר לשלב הבא"
    res = nearest_resource(state)
    if res is not None:
        info = CATALOG.resource(res.kind)
        if info.tool and info.tool not in inv.tools:
            return "%s - צריך %s" % (info.name, CATALOG.tool(info.tool).name)
        if res.ready_at > state.now:
            return "%s - עוד לא מוכן" % info.name
        return "Q = %s" % info.name
    tile = nearest_fish_tile(state)
    if tile is not None:
        if "rod" not in inv.tools:
            return "מים עם דגים - צריך חכה"
        if state.level.fish_cooldown.get(tile, 0) > state.now:
            return "מים עם דגים - עוד לא חזרו"
        return "Q = דיג"
    if nearby_crate(state) is not None:
        return "Q = פתיחת תיבה"
    return ""
