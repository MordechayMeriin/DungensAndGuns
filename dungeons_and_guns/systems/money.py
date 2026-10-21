# -*- coding: utf-8 -*-
"""הכסף: 4 סוגים - מטבע, דולר (10 מטבעות), מטיל זהב (10 דולר) ויהלום (10 מטילי זהב).

כל הסכומים במשחק (מחירים, פרסים) נמדדים במטבעות. כשמקבלים כסף הוא מגיע בהכי מעט פריטים,
כשמשלמים - משלמים קודם מהכסף הקטן ומקבלים עודף, ובתיק (E) אפשר להחליף בין הסוגים.
"""

from ..models import Coin, GameState, SMALL_TO_BIG

NAMES = {Coin.COIN: ("מטבע", "מטבעות"), Coin.DOLLAR: ("דולר", "דולר"),
         Coin.GOLD: ("מטיל זהב", "מטילי זהב"), Coin.DIAMOND: ("יהלום", "יהלומים")}


def coin_name(coin: Coin, count: int = 1) -> str:
    one, many = NAMES[coin]
    return one if count == 1 else many


def parts_text(parts: dict[Coin, int]) -> str:
    """{דולר: 3, מטבע: 7} -> "3 דולר ו-7 מטבעות" (מהגדול לקטן)."""
    items = ["%d %s" % (n, coin_name(c, n)) for c in reversed(SMALL_TO_BIG) if (n := parts.get(c, 0))]
    if not items:
        return "כלום"
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " ו-" + items[-1]


def earn(state: GameState, amount: int) -> str:
    """נותן כסף ומחזיר טקסט להודעה ("3 דולר ו-7 מטבעות")."""
    return parts_text(state.inventory.earn(amount))


def pay(state: GameState, amount: int) -> str | None:
    """משלם. מחזיר טקסט על העודף ("" אם אין עודף), או None אם אין מספיק כסף."""
    receipt = state.inventory.pay(amount)
    if receipt is None:
        return None
    _, change = receipt
    return " (עודף: %s)" % parts_text(change) if any(change.values()) else ""


def wallet_text(state: GameState) -> str:
    inv = state.inventory
    return " | ".join("%s: %d" % (coin_name(c, 2), inv.coin_count(c)) for c in reversed(SMALL_TO_BIG))


def exchange(state: GameState, coin: Coin, up: bool) -> None:
    """בתיק: להחליף 10 בסוג הבא (up), או לפרוט 1 ל-10 מהסוג הקודם."""
    inv = state.inventory
    i = SMALL_TO_BIG.index(coin)
    if up:
        if inv.exchange_up(coin):
            state.play("pickup")
            state.say("החלפת 10 %s ב%s אחד" % (coin_name(coin, 10), coin_name(SMALL_TO_BIG[i + 1])))
        else:
            state.play("no", gap=300)
            state.say("צריך 10 %s כדי להחליף" % coin_name(coin, 10) if i < 3 else "יהלום הוא הכסף הכי גדול")
    elif inv.exchange_down(coin):
        state.play("pickup")
        state.say("פרטת %s ל-10 %s" % (coin_name(coin), coin_name(SMALL_TO_BIG[i - 1], 10)))
    else:
        state.play("no", gap=300)
        state.say("אין לך %s לפרוט" % coin_name(coin) if i > 0 else "מטבע הוא הכסף הכי קטן")
