# -*- coding: utf-8 -*-
"""ירי, מכות, רימונים, קליעים ופיצוצים."""

import math
import random

from ..data import CATALOG
from ..config import TILE
from ..models import (Bullet, Enemy, GameState, Grenade, MissionKind, SmokeCloud, Tile, Weapon,
                      WeaponCategory, WeaponKind)
from . import health, missions, particles, ranks
from .inventory import aim_bonus, current_weapon

GRENADE_FUSE_MS = 900
CHARGE_FUSE_MS = 3000           # לבנת חבלה: 3 שניות לברוח
SMOKE_DURATION_MS = 7000
PLAYER_HIT_RADIUS = 15
MELEE_ARC = 1.1                 # חצי זווית המכה, ברדיאנים

# איזה קול משמיע כל סוג נשק
CAT_SOUNDS = {
    WeaponCategory.PISTOLS: "shot_pistol", WeaponCategory.SHOTGUNS: "shot_shotgun",
    WeaponCategory.SMGS: "shot_smg", WeaponCategory.RIFLES: "shot_rifle",
    WeaponCategory.SNIPERS: "shot_sniper", WeaponCategory.HEAVY: "shot_mg",
}


def weapon_sound(weapon: Weapon, enemy: bool = False) -> str:
    if weapon.kind == WeaponKind.MELEE:
        return "swing"
    if weapon.kind == WeaponKind.THROW:
        return "throw"
    if weapon.kind == WeaponKind.PLACE:
        return "tick"
    if weapon.art in ("bow", "sling", "shuriken"):
        return "shot_" + weapon.art
    name = CAT_SOUNDS.get(weapon.cat, "shot_pistol")
    return name.replace("shot_", "enemy_") if enemy else name


# ---------- השחקן תוקף ----------
def player_shoot(state: GameState) -> None:
    player, inv = state.player, state.inventory
    w = current_weapon(state)
    if w is None or state.now - player.last_shot < w.cooldown:
        return
    player.last_shot = state.now

    if w.is_throwable:
        if inv.throwable_count(w.id) <= 0:
            state.play("no", gap=400)
            state.say("נגמרו לך ה%s - קנה בחנות!" % w.name)
            return
        inv.throwables[w.id] -= 1
        state.play(weapon_sound(w))
        if w.kind == WeaponKind.PLACE:
            place_charge(state, w)
        else:
            throw_grenade(state, w)
        return

    ammo = CATALOG.ammo_for(w)
    poisoned = False
    if ammo:
        if inv.ammo_count(ammo.id) <= 0:
            state.play("no", gap=500)
            state.say("נגמרו לך %s! קנה בחנות או החלף נשק" % ammo.name)
            return
        inv.ammo[ammo.id] -= 1
        if ammo.id == CATALOG.poison.ammo and inv.poison_arrows > 0:
            inv.poison_arrows -= 1
            poisoned = True

    state.play(weapon_sound(w), gap=40)
    if w.kind == WeaponKind.MELEE:
        swing(state, w)
        return

    acc_bonus, rng_bonus = aim_bonus(inv)
    acc = min(0.99, w.acc + acc_bonus)
    if player.hp_ratio <= 0.25:
        acc *= 0.8                      # מד חיים אדום - קשה יותר לכוון
    rng = w.rng * (1.0 + rng_bonus)
    for _ in range(w.pellets):
        dx, dy = player.dir
        if w.pellets > 1:
            angle = math.atan2(dy, dx) + random.uniform(-0.2, 0.2)
            dx, dy = math.cos(angle), math.sin(angle)
        state.level.bullets.append(Bullet(x=player.x, y=player.y, dx=dx, dy=dy, speed=w.speed,
                                          dmg=w.dmg, acc=acc, rng=rng, from_player=True,
                                          poison=poisoned))


def swing(state: GameState, w: Weapon) -> None:
    """מכה בנשק קר - פוגעת בכל אויב קרוב בכיוון שאליו אתה מסתכל."""
    player, level = state.player, state.level
    player.swing_until = state.now + 150
    reach = w.rng
    player.swing_reach = reach
    face = math.atan2(player.dir[1], player.dir[0])
    hit = False
    for e in list(level.enemies):
        if math.hypot(e.x - player.x, e.y - player.y) > reach + e.r:
            continue
        angle = math.atan2(e.y - player.y, e.x - player.x)
        if abs((angle - face + math.pi) % (2 * math.pi) - math.pi) > MELEE_ARC:
            continue
        hit = True
        particles.spark(level, e.x, e.y, (255, 240, 170))
        damage_enemy(state, e, random.uniform(*w.dmg))
    if not hit:
        particles.spark(level, player.x + player.dir[0] * reach,
                        player.y + player.dir[1] * reach, (140, 140, 150))


def throw_grenade(state: GameState, w: Weapon) -> None:
    player = state.player
    launcher = "launcher" in state.inventory.gear
    boost = 1.5 if launcher else 1.0
    state.level.grenades.append(Grenade(
        x=player.x, y=player.y, dx=player.dir[0], dy=player.dir[1], speed=6.0 * boost,
        weapon=w, fuse=state.now + GRENADE_FUSE_MS, rng=w.rng * boost,
        radius=w.radius * (1.4 if launcher else 1.0)))


def place_charge(state: GameState, w: Weapon) -> None:
    """לבנת חבלה נשארת איפה שעומדים, ומתפוצצת אחרי 3 שניות - צריך לברוח!"""
    player = state.player
    state.level.grenades.append(Grenade(
        x=player.x, y=player.y, dx=0, dy=0, speed=0, weapon=w,
        fuse=state.now + CHARGE_FUSE_MS, rng=0, radius=w.radius))
    state.say("הנחת %s - ברח! בום בעוד 3 שניות" % w.name)


def break_walls(state: GameState, gr: Grenade) -> None:
    """לבנת חבלה שוברת את הקירות שצמודים למשבצת שלה (לא את קיר המסגרת ולא שערים)."""
    level, power = state.level, gr.weapon.wall_power
    gx, gy = int(gr.x // TILE), int(gr.y // TILE)
    broken = blocked = 0
    for tx, ty in ((gx + 1, gy), (gx - 1, gy), (gx, gy + 1), (gx, gy - 1)):
        if not (0 < tx < level.cols - 1 and 0 < ty < level.rows - 1):
            continue                                    # המסגרת של המבוך לא נשברת
        tile = level.grid[ty][tx]
        if tile == Tile.WALL or (tile == Tile.ARMORED and power >= 2):
            level.grid[ty][tx] = Tile.FLOOR
            broken += 1
            particles.burst(level, tx * TILE + TILE / 2, ty * TILE + TILE / 2, 14, 3.5, 26,
                            ((120, 120, 132), (90, 90, 100), (160, 150, 130)))
        elif tile == Tile.ARMORED:
            blocked += 1
    if broken:
        state.say("הקיר נשבר!" if broken == 1 else "%d קירות נשברו!" % broken)
    elif blocked:
        state.say("%s לא שובר קיר משוריין - צריך סמטקס" % gr.weapon.name)


# ---------- פגיעה באויבים ----------
def damage_enemy(state: GameState, e: Enemy, amount: float) -> None:
    """פגיעה רגילה (קליע או מכה): אם האויב מת, מקבלים כסף ואולי גם תחמושת."""
    e.hp -= amount
    state.play("hit", gap=30)
    if e.hp <= 0:
        kill_enemy(state, e, 20, 50, "חיסלת אויב", loot=True)


def poison_enemy(state: GameState, e: Enemy) -> None:
    """חץ מורעל פגע: מעכשיו האויב מאבד חיים כל שנייה, לכמה שניות."""
    e.poison_until = state.now + CATALOG.poison.seconds * 1000
    e.poison_tick = state.now
    particles.spark(state.level, e.x, e.y, (120, 230, 90))


def update_poison(state: GameState) -> None:
    """כל שנייה - אויבים מורעלים מאבדים חיים. מי שמת מהרעל שווה כסף ונקודות כרגיל."""
    level, dps = state.level, CATALOG.poison.dps
    for e in list(level.enemies):
        if e.poison_until <= e.poison_tick or state.now - e.poison_tick < 1000:
            continue
        e.poison_tick += 1000
        e.hp -= dps
        particles.spark(level, e.x, e.y - e.r, (120, 230, 90))
        if e.hp <= 0:
            kill_enemy(state, e, 20, 50, "האויב מת מהרעל")


def kill_enemy(state: GameState, e: Enemy, low: int, high: int, headline: str,
               loot: bool = False) -> None:
    """אויב מת: כסף, נקודות דרגה (לפי הנשק שלו) ואולי גם התחמושת שלו."""
    state.play("enemy_die")
    state.level.enemies.remove(e)
    gain = random.randint(low, high)
    state.inventory.money += gain
    points, promoted = ranks.award_kill(state, e.weapon)
    extra = loot_ammo(state, e) if loot else ""
    state.say("%s! +%d כסף +%d נקודות%s" % (headline, gain, points, extra))
    if promoted:
        ranks.announce_promotion(state, promoted)
    missions.progress(state, MissionKind.KILL)


def loot_ammo(state: GameState, enemy: Enemy) -> str:
    """בסיכוי מסוים לוקחים מהאויב את התחמושת שהייתה לו."""
    ammo = CATALOG.ammo_for(enemy.weapon)
    if not ammo or random.random() > 0.45:
        return ""
    count = max(2, ammo.pack // 4)
    state.inventory.add_ammo(ammo.id, count)
    return " ולקחת %d %s" % (count, ammo.name)


# ---------- עדכון בכל פריים ----------
def update_bullets(state: GameState) -> None:
    level, player = state.level, state.player
    for b in level.bullets:
        nx, ny = b.x + b.dx * b.speed, b.y + b.dy * b.speed
        b.traveled += b.speed
        if level.is_wall(nx, ny) or b.traveled > b.rng:
            b.dead = True
            particles.spark(level, nx, ny, (140, 140, 140))
            continue
        b.x, b.y = nx, ny

        if b.from_player:
            for e in level.enemies:
                if math.hypot(b.x - e.x, b.y - e.y) < e.r + 4:
                    b.dead = True
                    if random.random() < b.acc:
                        particles.spark(level, b.x, b.y, (255, 204, 51))
                        damage_enemy(state, e, random.uniform(*b.dmg))
                        if b.poison and e in level.enemies:
                            poison_enemy(state, e)
                    else:
                        particles.spark(level, b.x, b.y, (150, 150, 150))
                    break
        elif player.invuln <= 0 and math.hypot(b.x - player.x, b.y - player.y) < PLAYER_HIT_RADIUS:
            b.dead = True
            if random.random() < b.acc:
                health.hurt(state, random.uniform(*b.dmg))
                particles.spark(level, b.x, b.y, (255, 68, 68))
                state.play("hurt", gap=60)
            else:
                particles.spark(level, b.x, b.y, (150, 150, 150))
    level.bullets = [b for b in level.bullets if not b.dead]


def update_grenades(state: GameState) -> None:
    level = state.level
    for gr in level.grenades:
        if gr.speed > 0.25:
            nx, ny = gr.x + gr.dx * gr.speed, gr.y + gr.dy * gr.speed
            if level.is_wall(nx, ny):
                gr.dx, gr.dy = -gr.dx * 0.5, -gr.dy * 0.5      # מקפץ מהקיר
            else:
                gr.x, gr.y = nx, ny
                gr.traveled += gr.speed
            gr.speed *= 0.94
            if gr.traveled > gr.rng:
                gr.speed = 0
        if state.now >= gr.fuse:
            gr.dead = True
            explode(state, gr)
    level.grenades = [g for g in level.grenades if not g.dead]


def explode(state: GameState, gr: Grenade) -> None:
    level, player = state.level, state.player
    if gr.weapon.id == "smoke":
        state.play("hiss")
        level.smokes.append(SmokeCloud(x=gr.x, y=gr.y, r=gr.radius,
                                       until=state.now + SMOKE_DURATION_MS))
        particles.burst(level, gr.x, gr.y, 24, 2.2, 40, ((196, 198, 204),))
        state.say("ענן עשן! האויבים לא רואים אותך")
        return

    state.play("explosion")
    particles.burst(level, gr.x, gr.y, 30, 5, 24,
                    ((255, 172, 44), (252, 96, 40), (250, 230, 130)))
    for e in list(level.enemies):
        d = math.hypot(e.x - gr.x, e.y - gr.y)
        if d <= gr.radius:
            e.hp -= random.uniform(*gr.weapon.dmg) * (1 - d / gr.radius * 0.6)
            if e.hp <= 0:
                kill_enemy(state, e, 25, 60, "פיצצת אויב")
    if gr.weapon.wall_power:
        break_walls(state, gr)
    d = math.hypot(player.x - gr.x, player.y - gr.y)
    if d <= gr.radius and player.invuln <= 0:
        health.hurt(state, random.uniform(*gr.weapon.dmg) * 0.5 * (1 - d / gr.radius * 0.6))
        state.say("נפגעת מה%s שלך!" % gr.weapon.name)


def update_smokes(state: GameState) -> None:
    state.level.smokes = [c for c in state.level.smokes if c.until > state.now]


def in_smoke(state: GameState) -> bool:
    player = state.player
    return any(math.hypot(player.x - c.x, player.y - c.y) < c.r for c in state.level.smokes)
