# -*- coding: utf-8 -*-
"""חיים, מחלה, תרופות ואוכל."""

from ..data import CATALOG
from ..models import GameState
from .inventory import damage_multiplier

SICK_TICK_MS = 1800
SICK_NAG_MS = 7000
POTION_COOLDOWN_MS = 350
MEAL_COOLDOWN_MS = 350


def _check_death(state: GameState) -> None:
    if state.player.hp <= 0:
        state.player.hp = 0
        if not state.game_over:
            state.game_over = True
            state.play("gameover")


def hurt(state: GameState, amount: float) -> None:
    """נזק מאויב/פיצוץ - המגן, השכפ"ץ והקסדה מקטינים אותו."""
    state.player.hp -= amount * damage_multiplier(state.inventory)
    _check_death(state)


def drain(state: GameState, amount: float) -> None:
    """נזק שהציוד לא עוצר (מחלה, כוויה)."""
    state.player.hp -= amount
    _check_death(state)


def infect(state: GameState) -> None:
    player = state.player
    player.sick = True
    player.sick_tick = state.now
    player.sick_nag = state.now
    state.play("sick")


def update_sickness(state: GameState) -> None:
    """המחלה מורידה חיים כל כמה שניות עד ששותים תרופה גדולה."""
    player = state.player
    if not player.sick or state.game_over:
        return
    if state.now - player.sick_tick > SICK_TICK_MS:
        player.sick_tick = state.now
        drain(state, 2)
    if state.now - player.sick_nag > SICK_NAG_MS:
        player.sick_nag = state.now
        state.say("אתה חולה! שתה תרופה גדולה (T)")


def drink_potion(state: GameState, potion_id: str | None = None) -> None:
    """שותה תרופה, רק אם חסרים חיים. בלי potion_id (מקש T) - הגדולה ביותר שיש."""
    player, inv = state.player, state.inventory
    if state.now - player.last_potion < POTION_COOLDOWN_MS:
        return
    player.last_potion = state.now
    if player.hp >= player.max_hp and not player.sick:
        state.play("no", gap=400)
        state.say("החיים שלך מלאים")
        return
    if player.sick and inv.potion_count("large") <= 0:
        state.play("no", gap=400)
        state.say("אתה חולה - רק תרופה גדולה תעזור, וקנית רק קטנות")
        return
    if potion_id is None:
        order = ("large",) if player.sick else ("large", "medium", "small")
    elif player.sick and potion_id != "large":
        state.play("no", gap=400)
        state.say("אתה חולה - רק תרופה גדולה תעזור")
        return
    else:
        order = (potion_id,)
    for pid in order:
        if inv.potion_count(pid) > 0:
            potion = CATALOG.potion(pid)
            inv.potions[pid] -= 1
            player.hp = min(player.max_hp, player.hp + potion.heal)
            state.play("potion")
            if pid == "large" and player.sick:
                player.sick = False
                state.say("שתית תרופה גדולה, הבראת מהמחלה! +%d חיים" % potion.heal)
            else:
                state.say("שתית %s! +%d חיים" % (potion.name, potion.heal))
            return
    state.play("no", gap=400)
    if potion_id is None:
        state.say("אין לך תרופות - קנה בחנות!")
    else:
        state.say("נגמרה לך %s - קנה בחנות!" % CATALOG.potion(potion_id).name)


def eat(state: GameState, food_id: str | None = None) -> None:
    """אוכל. בלי food_id (מקש F) - המנה שהכי מתאימה לחיים שחסרים (בלי לבזבז עוגה על שריטה).

    אוכל לא מרפא מחלה - בשביל זה צריך תרופה גדולה.
    """
    player, inv = state.player, state.inventory
    if state.now - player.last_meal < MEAL_COOLDOWN_MS:
        return
    player.last_meal = state.now
    have = [f for f in CATALOG.foods if inv.food_count(f.id) > 0
            and (food_id is None or f.id == food_id)]
    if not have:
        state.play("no", gap=400)
        state.say("אין לך אוכל - הכן בסדנה (Y)")
        return
    if player.hp >= player.max_hp:
        state.play("no", gap=400)
        state.say("אתה שבע - החיים שלך מלאים")
        return
    lacking = player.max_hp - player.hp
    enough = [f for f in have if f.heal >= lacking]
    food = min(enough, key=lambda f: f.heal) if enough else max(have, key=lambda f: f.heal)
    inv.food[food.id] -= 1
    if not inv.food[food.id]:
        del inv.food[food.id]
    player.hp = min(player.max_hp, player.hp + food.heal)
    state.play("potion")
    state.say("אכלת %s! +%d חיים" % (food.name, food.heal))
