# -*- coding: utf-8 -*-
"""דרגות: נקודות על כל אויב שמחסלים. כל דרגה פותחת בחנות נשק חזק יותר ומוסיפה קצת חיים."""

from ..data import CATALOG
from ..models import GameState, Rank, Weapon

BASE_POINTS = 5         # כל אויב שווה לפחות את זה
PRICE_PER_POINT = 40    # ועוד נקודה על כל 40 כסף שהנשק שלו שווה
BASE_MAX_HP = 100       # החיים המקסימליים של טוראי
HP_PER_RANK = 10        # כל דרגה מוסיפה עוד קצת


def kill_points(weapon: Weapon) -> int:
    """כמה נקודות מקבלים על אויב - ככל שהנשק שלו טוב (יקר) יותר, יותר נקודות."""
    return BASE_POINTS + weapon.price // PRICE_PER_POINT


def current_rank(state: GameState) -> Rank:
    return CATALOG.rank_for(state.player.points)


def rank_max_hp(state: GameState) -> int:
    """החיים המקסימליים לפי הדרגה: 100 לטוראי, ועוד 10 על כל דרגה."""
    return BASE_MAX_HP + HP_PER_RANK * CATALOG.ranks.index(current_rank(state))


def sync_max_hp(state: GameState) -> None:
    """מעדכן את החיים המקסימליים לפי הדרגה. החיים שנוספו מגיעים מלאים."""
    player, new_max = state.player, rank_max_hp(state)
    if new_max > player.max_hp:
        player.hp += new_max - player.max_hp
        player.max_hp = new_max


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
    if after == before:
        return None
    sync_max_hp(state)
    return after


def award_kill(state: GameState, weapon: Weapon) -> tuple[int, Rank | None]:
    """מוסיף נקודות על אויב שחוסל. מחזיר כמה נקודות, ואת הדרגה החדשה אם עלית בדרגה."""
    points = kill_points(weapon)
    return points, add_points(state, points)


def announce_promotion(state: GameState, rank: Rank) -> None:
    state.play("rank_up")
    hp = " | חיים מקסימליים: %d" % state.player.max_hp
    if rank.unlocks:
        names = ", ".join(CATALOG.weapon(wid).name for wid in rank.unlocks)
        state.say("עלית לדרגת %s! עכשיו אפשר לקנות: %s%s" % (rank.name, names, hp))
    else:
        state.say("עלית לדרגת %s!%s" % (rank.name, hp))
