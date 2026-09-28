# -*- coding: utf-8 -*-
"""דרגות: נקודות על כל אויב שמחסלים, ודרגות שפותחות בחנות נשק חזק יותר."""

from ..data import CATALOG
from ..models import GameState, Rank, Weapon

BASE_POINTS = 5         # כל אויב שווה לפחות את זה
PRICE_PER_POINT = 40    # ועוד נקודה על כל 40 כסף שהנשק שלו שווה


def kill_points(weapon: Weapon) -> int:
    """כמה נקודות מקבלים על אויב - ככל שהנשק שלו טוב (יקר) יותר, יותר נקודות."""
    return BASE_POINTS + weapon.price // PRICE_PER_POINT


def current_rank(state: GameState) -> Rank:
    return CATALOG.rank_for(state.player.points)


def rank_needed(state: GameState, weapon: Weapon) -> Rank | None:
    """הדרגה שחסרה כדי לקנות את הנשק, או None אם כבר מותר."""
    rank = CATALOG.unlock_rank(weapon.id)
    if rank is None or state.player.points >= rank.points:
        return None
    return rank


def add_points(state: GameState, points: int) -> Rank | None:
    """מוסיף נקודות דרגה. מחזיר את הדרגה החדשה אם עלית בדרגה."""
    before = current_rank(state)
    state.player.points += points
    after = current_rank(state)
    return after if after != before else None


def award_kill(state: GameState, weapon: Weapon) -> tuple[int, Rank | None]:
    """מוסיף נקודות על אויב שחוסל. מחזיר כמה נקודות, ואת הדרגה החדשה אם עלית בדרגה."""
    points = kill_points(weapon)
    return points, add_points(state, points)


def announce_promotion(state: GameState, rank: Rank) -> None:
    state.play("rank_up")
    if rank.unlocks:
        names = ", ".join(CATALOG.weapon(wid).name for wid in rank.unlocks)
        state.say("עלית לדרגת %s! עכשיו אפשר לקנות: %s" % (rank.name, names))
    else:
        state.say("עלית לדרגת %s!" % rank.name)
