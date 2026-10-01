# -*- coding: utf-8 -*-
"""ערפל: מדי פעם יורד ערפל לבערך דקה. בערפל רואים רק קרוב - וגם האויבים רואים רק קרוב."""

import random

from ..models import GameState

FOG_SIGHT = 120                         # כמה רחוק רואים בערפל (בפיקסלים, כ-4 משבצות)
FOG_MS = (40_000, 70_000)               # כמה זמן הערפל נשאר
CLEAR_MS = (90_000, 180_000)            # כמה זמן עובר בין ערפל לערפל
FADE_MS = 2000                          # הערפל יורד ומתפזר לאט


def foggy(state: GameState) -> bool:
    return state.now < state.weather.fog_until


def fog_strength(state: GameState) -> float:
    """0 = שקוף, 1 = ערפל מלא. בהתחלה ובסוף הוא נכנס ויוצא בהדרגה."""
    w = state.weather
    if not foggy(state):
        return 0.0
    return max(0.0, min(1.0, (state.now - w.fog_start) / FADE_MS, (w.fog_until - state.now) / FADE_MS))


def can_see(state: GameState, distance: float) -> bool:
    """האם רואים משהו במרחק הזה (בערפל - רק קרוב)."""
    return not foggy(state) or distance <= FOG_SIGHT


def update(state: GameState) -> None:
    """כל פריים: האם הגיע הזמן לערפל, או שהערפל נגמר."""
    w = state.weather
    if w.next_fog_at == 0:                  # משחק חדש - קובעים מתי יהיה הערפל הראשון
        w.next_fog_at = state.now + random.randint(*CLEAR_MS)
    if w.fog_until and state.now >= w.fog_until:
        w.fog_until = 0
        state.say("הערפל התפזר")
    elif not foggy(state) and state.now >= w.next_fog_at:
        w.fog_start = state.now
        w.fog_until = state.now + random.randint(*FOG_MS)
        w.next_fog_at = w.fog_until + random.randint(*CLEAR_MS)
        state.play("hiss")
        state.say("ירד ערפל! רואים רק קרוב - וגם האויבים לא רואים אותך מרחוק")
