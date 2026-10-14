# -*- coding: utf-8 -*-
"""ערפל: מדי פעם יורד ערפל על אזור במבוך לבערך דקה - לפעמים עליך, ולפעמים במקום אחר.

בתוך הערפל רואים רק קרוב: אם אתה או האויב בתוך הערפל, הוא רואה אותך (ואתה אותו) רק מקרוב.
"""

import math
import random

from ..config import TILE
from ..models import GameState, Tile

FOG_SIGHT = 120                         # כמה רחוק רואים בערפל (בפיקסלים, כ-4 משבצות)
FOG_RADIUS = (5 * TILE, 16 * TILE)      # כמה גדול אזור הערפל (16 משבצות - כמעט כל המבוך)
FOG_MS = (40_000, 70_000)               # כמה זמן הערפל נשאר
CLEAR_MS = (90_000, 180_000)            # כמה זמן עובר בין ערפל לערפל
FADE_MS = 2000                          # הערפל יורד ומתפזר לאט


def foggy(state: GameState) -> bool:
    """האם יש עכשיו ערפל איפשהו במבוך."""
    return state.now < state.weather.fog_until


def fog_strength(state: GameState) -> float:
    """0 = שקוף, 1 = ערפל מלא. בהתחלה ובסוף הוא נכנס ויוצא בהדרגה."""
    w = state.weather
    if not foggy(state):
        return 0.0
    return max(0.0, min(1.0, (state.now - w.fog_start) / FADE_MS, (w.fog_until - state.now) / FADE_MS))


def in_fog(state: GameState, x: float, y: float) -> bool:
    w = state.weather
    return foggy(state) and math.hypot(x - w.fog_x, y - w.fog_y) <= w.fog_r


def can_see(state: GameState, x: float, y: float) -> bool:
    """האם השחקן ומי שעומד ב-(x, y) רואים זה את זה: בערפל - רק מקרוב."""
    player = state.player
    if math.hypot(x - player.x, y - player.y) <= FOG_SIGHT:
        return True
    return not (in_fog(state, x, y) or in_fog(state, player.x, player.y))


def update(state: GameState) -> None:
    """כל פריים: האם הגיע הזמן לערפל, או שהערפל נגמר."""
    w = state.weather
    if w.next_fog_at == 0:                  # משחק חדש - קובעים מתי יהיה הערפל הראשון
        w.next_fog_at = state.now + random.randint(*CLEAR_MS)
    if w.fog_until and state.now >= w.fog_until:
        w.fog_until = 0
        state.say("הערפל התפזר")
    elif not foggy(state) and state.now >= w.next_fog_at:
        start_fog(state)


def start_fog(state: GameState) -> None:
    """ערפל יורד על אזור אקראי במבוך."""
    w, level = state.weather, state.level
    floor = [(x, y) for y, row in enumerate(level.grid) for x, t in enumerate(row) if t == Tile.FLOOR]
    tx, ty = random.choice(floor)
    w.fog_x, w.fog_y = tx * TILE + TILE / 2, ty * TILE + TILE / 2
    w.fog_r = random.randint(*FOG_RADIUS)
    w.fog_start = state.now
    w.fog_until = state.now + random.randint(*FOG_MS)
    w.next_fog_at = w.fog_until + random.randint(*CLEAR_MS)
    state.play("hiss")
    if in_fog(state, state.player.x, state.player.y):
        state.say("ירד עליך ערפל! רואים רק קרוב - וגם האויבים לא רואים אותך מרחוק")
    else:
        state.say("ירד ערפל באזור אחר של המבוך")
