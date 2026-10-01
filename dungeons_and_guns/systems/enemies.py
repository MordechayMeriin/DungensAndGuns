# -*- coding: utf-8 -*-
"""התנהגות האויבים: מתקרבים לשחקן עד לטווח הנשק שלהם, יורים, וזורקים רימונים.

ציוד של אויב עובד כמו אצל השחקן: לייזר וכוונת מוסיפים דיוק, מגן מאט אותו.
בערפל אויב רואה רק קרוב.
"""

import math
import random

from ..data import CATALOG
from ..models import Bullet, Enemy, GameState, Grenade
from . import weather
from .combat import ENEMY_GRENADE_FUSE_MS, in_smoke, weapon_sound
from .inventory import gear_items

ENEMY_BULLET_SPEED = 7
THROW_RANGE = (60, 150)         # מאיזה מרחק אויב זורק רימון
THROW_COOLDOWN_MS = 5000
THROW_CHANCE = 0.02             # בכל פריים שאפשר - כדי שלא כולם יזרקו מיד


def update_enemies(state: GameState) -> None:
    level, player = state.level, state.player
    hidden = in_smoke(state)
    for e in level.enemies:
        d = max(1.0, math.hypot(player.x - e.x, player.y - e.y))
        if not weather.can_see(state, d):
            continue                        # בערפל - לא רואה אותך, אז לא רודף ולא יורה
        w = e.weapon
        gear = gear_items(e.gear)
        acc = min(0.99, w.acc + sum(g.acc for g in gear))
        rng = w.rng * (1.0 + sum(g.rng for g in gear))
        if e.grenades.get("smoke") and e.hp < e.max_hp * 0.5:
            throw_smoke(state, e)
        elif not hidden:
            maybe_throw_grenade(state, e, d)
        if d > rng * 0.55:
            dx, dy = (player.x - e.x) / d, (player.y - e.y) / d
            speed = (1.0 + level.number * 0.03) * max(0.5, 1.0 - sum(g.slow for g in gear))
            if level.can_move(e.x + dx * speed, e.y, e.r):
                e.x += dx * speed
            if level.can_move(e.x, e.y + dy * speed, e.r):
                e.y += dy * speed
        if d <= rng and state.now - e.last_shot > w.cooldown and not hidden:
            e.last_shot = state.now
            state.play(weapon_sound(w, enemy=True), gap=70)
            dx, dy = (player.x - e.x) / d, (player.y - e.y) / d
            level.bullets.append(Bullet(x=e.x, y=e.y, dx=dx, dy=dy, speed=ENEMY_BULLET_SPEED,
                                        dmg=w.dmg, acc=acc, rng=rng, from_player=False))


def maybe_throw_grenade(state: GameState, e: Enemy, d: float) -> None:
    """אויב עם רימון יד זורק אותו כשאתה קרוב (אבל לא צמוד)."""
    if (not e.grenades.get("grenade") or not THROW_RANGE[0] < d < THROW_RANGE[1]
            or state.now - e.last_throw < THROW_COOLDOWN_MS or random.random() > THROW_CHANCE):
        return
    player, w = state.player, CATALOG.weapon("grenade")
    e.grenades["grenade"] -= 1
    e.last_throw = state.now
    # המהירות דועכת פי 0.94 כל פריים, אז מהירות של d*0.06 עוצרת בערך עליך
    state.level.grenades.append(Grenade(
        x=e.x, y=e.y, dx=(player.x - e.x) / d, dy=(player.y - e.y) / d, speed=d * 0.06,
        weapon=w, fuse=state.now + ENEMY_GRENADE_FUSE_MS, rng=d, radius=w.radius, from_enemy=True))
    state.play("throw")
    state.say("אויב זרק עליך רימון - ברח!")


def throw_smoke(state: GameState, e: Enemy) -> None:
    """אויב פצוע זורק רימון עשן ליד עצמו כדי להסתתר: קשה לפגוע בו בתוך העשן."""
    w = CATALOG.weapon("smoke")
    e.grenades["smoke"] -= 1
    e.last_throw = state.now
    state.level.grenades.append(Grenade(
        x=e.x, y=e.y, dx=0, dy=0, speed=0, weapon=w, fuse=state.now + 300, rng=0,
        radius=w.radius, from_enemy=True))
    state.play("throw")
