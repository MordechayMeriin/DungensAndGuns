# -*- coding: utf-8 -*-
"""התנהגות האויבים: מתקרבים לשחקן עד לטווח הנשק שלהם, ויורים."""

import math

from ..models import Bullet, GameState
from .combat import in_smoke, weapon_sound

ENEMY_BULLET_SPEED = 7


def update_enemies(state: GameState) -> None:
    level, player = state.level, state.player
    hidden = in_smoke(state)
    for e in level.enemies:
        d = max(1.0, math.hypot(player.x - e.x, player.y - e.y))
        w = e.weapon
        if d > w.rng * 0.55:
            dx, dy = (player.x - e.x) / d, (player.y - e.y) / d
            speed = 1.0 + level.number * 0.03
            if level.can_move(e.x + dx * speed, e.y, e.r):
                e.x += dx * speed
            if level.can_move(e.x, e.y + dy * speed, e.r):
                e.y += dy * speed
        if d <= w.rng and state.now - e.last_shot > w.cooldown and not hidden:
            e.last_shot = state.now
            state.play(weapon_sound(w, enemy=True), gap=70)
            dx, dy = (player.x - e.x) / d, (player.y - e.y) / d
            level.bullets.append(Bullet(x=e.x, y=e.y, dx=dx, dy=dy, speed=ENEMY_BULLET_SPEED,
                                        dmg=w.dmg, acc=w.acc, rng=w.rng, from_player=False))
