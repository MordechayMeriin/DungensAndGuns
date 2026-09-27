# -*- coding: utf-8 -*-
"""גלגל המזל: סיבוב, עצירה ומתן הפרס (או העונש)."""

import math
import random

from ..data import CATALOG
from ..models import GameState, WheelOutcome, WheelSlice, WheelSpin
from . import health
from .inventory import give_random_gear, give_random_tool, give_weapon

FRICTION = 0.975            # בערך שלוש שניות סיבוב
STOP_SPEED = 0.005


def spin(state: GameState) -> None:
    state.wheel = WheelSpin(angle=random.uniform(0, 6.28), speed=random.uniform(0.34, 0.46))
    state.play("buy")


def slice_under_pointer(angle: float) -> int:
    """איזו משבצת נמצאת מתחת לחץ שבראש הגלגל."""
    count = len(CATALOG.wheel_slices)
    step = 2 * math.pi / count
    rel = (-math.pi / 2 - angle) % (2 * math.pi)
    return int(rel // step) % count


def update(state: GameState) -> None:
    w = state.wheel
    if w is None or w.done:
        return
    w.angle = (w.angle + w.speed) % (2 * math.pi)
    w.speed *= FRICTION
    index = slice_under_pointer(w.angle)
    if index != w.last_index:
        w.last_index = index
        state.play("tick", gap=20)
    if w.speed < STOP_SPEED:
        w.done = True
        w.result = CATALOG.wheel_slices[index]
        w.text = apply(state, w.result)


def close(state: GameState) -> None:
    """אחרי שהגלגל עצר, כל מקש/קליק סוגר אותו."""
    if state.wheel is not None and state.wheel.done:
        state.wheel = None


def apply(state: GameState, slice_: WheelSlice) -> str:
    """מחלק את הפרס או את העונש לפי המשבצת שיצאה, ומחזיר את הטקסט להצגה."""
    inv, player = state.inventory, state.player
    state.play("crate_good" if slice_.good else "crate_bad")

    match slice_.id:
        case WheelOutcome.MONEY:
            gain = random.randint(150, 250 + state.level.number * 40)
            inv.money += gain
            return "זכית ב-%d כסף!" % gain
        case WheelOutcome.POTION:
            potion = CATALOG.potion(random.choice(["small", "medium", "large", "large"]))
            inv.add_potion(potion.id, 2)
            return "זכית ב-2 %s!" % potion.name
        case WheelOutcome.GRENADES:
            if random.random() < 0.5:
                ammo = random.choice(CATALOG.ammo_types)
                count = ammo.pack * 2
                inv.add_ammo(ammo.id, count)
                return "זכית ב-%d %s!" % (count, ammo.name)
            item = random.choice(CATALOG.throwables)
            count = random.randint(2, 4)
            inv.add_throwable(item.id, count)
            return "זכית ב-%d %s!" % (count, item.name)
        case WheelOutcome.WEAPON:
            # קודם בוחרים מחלקה באקראי, ואז נשק מתוכה - כך לכל מחלקה סיכוי שווה
            missing = [w for w in CATALOG.weapons
                       if not w.is_throwable and w.id not in inv.weapons]
            cats = sorted(set(w.cat for w in missing))
            if not cats:
                inv.money += 300
                return "יש לך כבר את כל הנשקים - קיבלת 300 כסף"
            cat = random.choice(cats)
            weapon = random.choice([w for w in missing if w.cat == cat])
            give_weapon(inv, weapon)
            return "זכית בנשק: %s (%s)!" % (weapon.name, weapon.cat)
        case WheelOutcome.TOOL:
            tool = give_random_tool(inv)
            if tool is None:
                inv.money += 200
                return "יש לך כבר את כל הכלים - קיבלת 200 כסף"
            return "זכית בכלי: %s!" % tool.name
        case WheelOutcome.GEAR:
            item = give_random_gear(inv)
            if item is None:
                inv.money += 300
                return "יש לך כבר את כל הציוד - קיבלת 300 כסף"
            return "זכית בציוד: %s!" % item.name
        case WheelOutcome.HEAL:
            player.hp = player.max_hp
            return "החיים שלך חזרו למלא!"
        case WheelOutcome.SICK:
            if player.sick:
                player.hp = max(1, player.hp - 10)
                return "עוד מחלה! -10 חיים"
            health.infect(state)
            return "נדבקת במחלה! צריך תרופה גדולה"
        case WheelOutcome.LOSE_MONEY:
            loss = min(inv.money, max(50, int(inv.money * random.uniform(0.2, 0.4))))
            inv.money -= loss
            return "הפסדת %d כסף" % loss
        case WheelOutcome.LOSE_HP:
            damage = random.randint(15, 30)
            state.play("hurt")
            health.hurt(state, damage)
            return "נפגעת! -%d חיים" % damage
