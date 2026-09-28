# -*- coding: utf-8 -*-
"""פתיחת תיבות: שלל, מלכודות או כלום."""

import random

from ..data import CATALOG
from ..models import Crate, CrateKind, GameState, MissionKind
from ..world import make_enemy
from . import health, missions, particles
from .inventory import give_random_gear, give_random_tool, give_weapon


def open_crate(state: GameState, crate: Crate) -> None:
    state.level.crates.remove(crate)
    if crate.kind == CrateKind.BAD:
        bad_crate(state, crate)
    elif crate.kind == CrateKind.EMPTY:
        state.play("crate_empty")
        particles.spark(state.level, crate.x, crate.y, (150, 150, 150))
        state.say("פתחת תיבה... והיא ריקה")
    else:
        good_crate(state, crate)
    missions.progress(state, MissionKind.CRATES)


def good_crate(state: GameState, crate: Crate) -> None:
    """שלל: כסף, תרופה, תחמושת, רימונים, נשק, כלי עבודה או ציוד."""
    inv, number = state.inventory, state.level.number
    state.play("crate_good")
    particles.spark(state.level, crate.x, crate.y, (255, 214, 102))
    roll = random.random()

    if roll < 0.07:
        inv.keys += 1
        state.say("בתיבה היה מפתח! (יש לך %d)" % inv.keys)
        return
    if roll < 0.30:
        gain = random.randint(20, 40 + number * 8)
        inv.money += gain
        state.say("פתחת תיבה! +%d כסף" % gain)
        return
    if roll < 0.50:
        potion = CATALOG.potion(random.choice(["small", "small", "medium", "large"]))
        inv.add_potion(potion.id)
        state.say("בתיבה הייתה %s!" % potion.name)
        return
    if roll < 0.58:
        ammo = random.choice(CATALOG.ammo_types)
        inv.add_ammo(ammo.id, ammo.pack)
        state.say("בתיבה היו %d %s!" % (ammo.pack, ammo.name))
        return
    if roll < 0.66:
        item = random.choice(CATALOG.throwables)
        count = random.randint(1, 3)
        inv.add_throwable(item.id, count)
        state.say("בתיבה היו %d %s!" % (count, item.name))
        return
    if roll < 0.82:
        budget = 400 + number * 300
        options = [w for w in CATALOG.weapons if not w.is_throwable
                   and w.id not in inv.weapons and w.price <= budget]
        if options:
            weapon = random.choice(options)
            give_weapon(inv, weapon)
            state.say("בתיבה היה נשק: %s!" % weapon.name)
            return
    if roll < 0.93:
        tool = give_random_tool(inv)
        if tool:
            state.say("בתיבה היה כלי: %s!" % tool.name)
            return
    else:
        item = give_random_gear(inv)
        if item:
            state.say("בתיבה היה ציוד: %s!" % item.name)
            return

    gain = random.randint(25, 50 + number * 8)       # אם אין מה לתת - כסף
    inv.money += gain
    state.say("פתחת תיבה! +%d כסף" % gain)


def bad_crate(state: GameState, crate: Crate) -> None:
    """תיבה רעה: מלכודת, אויבים, גז רעיל או גנב."""
    level, inv = state.level, state.inventory
    state.play("crate_bad")
    particles.burst(level, crate.x, crate.y, 16, 4, 22, ((232, 72, 60),))
    roll = random.random()

    if roll < 0.35:
        damage = random.randint(10, 25)
        state.play("explosion")
        health.hurt(state, damage)
        state.say("מלכודת בתיבה! -%d חיים" % damage)
    elif roll < 0.65:
        count = 1 if level.number < 4 else random.randint(1, 2)
        for _ in range(count):
            level.enemies.append(make_enemy(level, crate.x, crate.y))
        state.say("אויבים התחבאו בתיבה!")
    elif roll < 0.85:
        if state.player.sick:
            health.hurt(state, 8)
            state.say("עוד גז רעיל! -8 חיים")
        else:
            health.infect(state)
            state.say("גז רעיל בתיבה! נדבקת - צריך תרופה גדולה")
    else:
        loss = min(inv.money, max(15, int(inv.money * random.uniform(0.1, 0.3))))
        inv.money -= loss
        state.say("גנב היה בתיבה! -%d כסף" % loss)
