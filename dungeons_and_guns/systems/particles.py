# -*- coding: utf-8 -*-
"""ניצוצות קטנים שעפים מפגיעות, פיצוצים ותיבות."""

import random
from collections.abc import Sequence

from ..models import Level, Spark
from ..models.catalog import Color


def burst(level: Level, x: float, y: float, count: int, spread: float, life: int,
          colors: Sequence[Color]) -> None:
    for _ in range(count):
        level.sparks.append(Spark(x=x, y=y, vx=random.uniform(-spread, spread),
                                  vy=random.uniform(-spread, spread), life=life,
                                  color=random.choice(colors)))


def spark(level: Level, x: float, y: float, color: Color) -> None:
    burst(level, x, y, 5, 3, 18, (color,))


def update_sparks(level: Level) -> None:
    for s in level.sparks:
        s.x += s.vx
        s.y += s.vy
        s.life -= 1
    level.sparks = [s for s in level.sparks if s.life > 0]
