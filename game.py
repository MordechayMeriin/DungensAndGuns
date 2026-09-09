# -*- coding: utf-8 -*-
"""מבוך ונשק - משחק מבוך דו-ממדי מלמעלה."""

import math
import os
import random
import re
import sys

import pygame

TILE = 32
SCREEN_W, SCREEN_H = 960, 640
FPS = 60

COL_WALL = (58, 58, 68)
COL_FLOOR_A = (35, 35, 40)
COL_FLOOR_B = (38, 38, 44)
COL_PLAYER = (59, 120, 194)
COL_ENEMY = (194, 59, 59)
COL_EXIT = (232, 197, 58)
COL_CRATE = (138, 90, 42)
COL_TREE = (58, 157, 58)
COL_ORE = (138, 138, 149)
COL_TEXT = (235, 235, 235)
COL_PANEL = (30, 30, 34)
COL_PANEL_LINE = (100, 100, 110)

WEAPONS = [
    dict(id="glock",   name="גלוק 19",     cat="אקדחים",       dmg=(8, 14),   acc=0.80, rng=220, cooldown=280,  price=0),
    dict(id="p226",    name="SIG P226",    cat="אקדחים",       dmg=(10, 16),  acc=0.75, rng=240, cooldown=260,  price=120),
    dict(id="uzi",     name="עוזי",        cat="תתי מקלע",     dmg=(5, 9),    acc=0.55, rng=160, cooldown=90,   price=220),
    dict(id="mp5",     name="MP5",         cat="תתי מקלע",     dmg=(6, 10),   acc=0.60, rng=190, cooldown=100,  price=350),
    dict(id="m16",     name="M16",         cat="רובי סער",     dmg=(14, 20),  acc=0.65, rng=340, cooldown=170,  price=500),
    dict(id="ak47",    name="AK-47",       cat="רובי סער",     dmg=(16, 22),  acc=0.60, rng=320, cooldown=190,  price=520),
    dict(id="m249",    name="M249",        cat="מקלעים כבדים", dmg=(18, 26),  acc=0.45, rng=300, cooldown=110,  price=900),
    dict(id="m2",      name="M2 Browning", cat="מקלעים כבדים", dmg=(24, 32),  acc=0.40, rng=340, cooldown=140,  price=1300),
    dict(id="awp",     name="AWP",         cat="רובי צלפים",   dmg=(60, 80),  acc=0.92, rng=650, cooldown=1000, price=1600),
    dict(id="barrett", name="Barrett M82", cat="רובי צלפים",   dmg=(80, 100), acc=0.88, rng=700, cooldown=1200, price=2200),
]
WEAPON_CATS = ["אקדחים", "תתי מקלע", "רובי סער", "מקלעים כבדים", "רובי צלפים"]

TOOLS = [
    dict(id="saw",     name="מסור", desc="נדרש לאיסוף עצים",  price=80),
    dict(id="pickaxe", name="מכוש", desc="נדרש לכריית מכרות", price=80),
]

POTIONS = [
    dict(id="small",  name="תרופה קטנה",   heal=25,  price=40),
    dict(id="medium", name="תרופה בינונית", heal=60,  price=90),
    dict(id="large",  name="תרופה גדולה",  heal=120, price=160),
]

WEAPON_BY_ID = {w["id"]: w for w in WEAPONS}


LATIN_RUN = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-\./+%]*(?: [A-Za-z0-9\-\./+%]+)*")


def rtl(text):
    """מסדר טקסט עברי לתצוגה מימין לשמאל, בלי להפוך מספרים ומילים באנגלית."""
    parts = []
    idx = 0
    for match in LATIN_RUN.finditer(text):
        if match.start() > idx:
            parts.append(("he", text[idx:match.start()]))
        parts.append(("latin", match.group()))
        idx = match.end()
    if idx < len(text):
        parts.append(("he", text[idx:]))
    return "".join(s if kind == "latin" else s[::-1] for kind, s in reversed(parts))


def load_font(size, bold=False):
    for path in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\tahoma.ttf"):
        if os.path.exists(path):
            font = pygame.font.Font(path, size)
            font.set_bold(bold)
            return font
    return pygame.font.SysFont("arial", size, bold=bold)


class Bullet:
    def __init__(self, x, y, dx, dy, speed, dmg, acc, rng, from_player):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.speed = speed
        self.dmg = dmg
        self.acc = acc
        self.rng = rng
        self.traveled = 0.0
        self.from_player = from_player
        self.dead = False


class Enemy:
    def __init__(self, x, y, weapon, hp):
        self.x, self.y = x, y
        self.weapon = weapon
        self.hp = hp
        self.max_hp = hp
        self.r = 12
        self.last_shot = 0


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("מבוך ונשק")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = load_font(18)
        self.font_small = load_font(14)
        self.font_big = load_font(34, bold=True)
        self.reset_game()

    # ---------- מצב המשחק ----------
    def reset_game(self):
        self.level = 1
        self.hp = 100
        self.max_hp = 100
        self.money = 100
        self.owned_weapons = ["glock"]
        self.weapon_index = 0
        self.tools = {"saw": False, "pickaxe": False}
        self.potions = {"small": 0, "medium": 0, "large": 0}
        self.game_over = False
        self.shop_open = False
        self.shop_scroll = 0
        self.message = ""
        self.message_timer = 0
        self.last_shot = 0
        self.last_interact = 0
        self.build_level()

    def build_level(self):
        self.cols = 15 + self.level * 2 | 1
        self.rows = 11 + self.level * 2 | 1
        self.grid = self.generate_maze(self.cols, self.rows)

        free = [(x, y) for y in range(self.rows) for x in range(self.cols)
                if self.grid[y][x] == 0 and not (x <= 2 and y <= 2)]
        random.shuffle(free)

        self.px = TILE * 1.5
        self.py = TILE * 1.5
        self.dir = (0.0, 1.0)
        self.invuln = 60

        far = max(free, key=lambda t: t[0] + t[1])
        free.remove(far)
        self.exit_tile = far

        def take(n):
            out = []
            for _ in range(min(n, len(free))):
                out.append(free.pop())
            return out

        max_weapon = min(3 + self.level // 2, len(WEAPONS))
        self.enemies = []
        for (tx, ty) in take(min(3 + self.level, 12)):
            weapon = WEAPONS[random.randrange(max_weapon)]
            self.enemies.append(Enemy(tx * TILE + TILE / 2, ty * TILE + TILE / 2,
                                      weapon, 30 + self.level * 6))

        self.resources = []
        for i, (tx, ty) in enumerate(take(6 + self.level)):
            kind = "tree" if i % 2 == 0 else "ore"
            self.resources.append(dict(x=tx * TILE + TILE / 2, y=ty * TILE + TILE / 2, kind=kind))

        self.crates = [dict(x=tx * TILE + TILE / 2, y=ty * TILE + TILE / 2)
                       for (tx, ty) in take(3 + self.level // 2)]

        self.bullets = []
        self.sparks = []

    def generate_maze(self, w, h):
        grid = [[1] * w for _ in range(h)]
        stack = [(1, 1)]
        grid[1][1] = 0
        while stack:
            cx, cy = stack[-1]
            options = []
            for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                nx, ny = cx + dx, cy + dy
                if 0 < nx < w - 1 and 0 < ny < h - 1 and grid[ny][nx] == 1:
                    options.append((nx, ny, dx, dy))
            if options:
                nx, ny, dx, dy = random.choice(options)
                grid[cy + dy // 2][cx + dx // 2] = 0
                grid[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        return grid

    # ---------- עזרים ----------
    def weapon(self):
        return WEAPON_BY_ID[self.owned_weapons[self.weapon_index]]

    def is_wall(self, px, py):
        gx, gy = int(px // TILE), int(py // TILE)
        if gx < 0 or gy < 0 or gx >= self.cols or gy >= self.rows:
            return True
        return self.grid[gy][gx] == 1

    def can_move(self, x, y, r):
        return not (self.is_wall(x - r, y - r) or self.is_wall(x + r, y - r) or
                    self.is_wall(x - r, y + r) or self.is_wall(x + r, y + r))

    def say(self, text):
        self.message = text
        self.message_timer = 120

    def now(self):
        return pygame.time.get_ticks()

    # ---------- שחקן ----------
    def update_player(self, keys):
        if self.invuln > 0:
            self.invuln -= 1
        dx = dy = 0.0
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if dx or dy:
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            self.dir = (dx, dy)
            speed = 2.6
            if self.can_move(self.px + dx * speed, self.py, 11):
                self.px += dx * speed
            if self.can_move(self.px, self.py + dy * speed, 11):
                self.py += dy * speed

        if keys[pygame.K_SPACE]:
            self.shoot()
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.interact()

    def shoot(self):
        w = self.weapon()
        if self.now() - self.last_shot < w["cooldown"]:
            return
        self.last_shot = self.now()
        self.bullets.append(Bullet(self.px, self.py, self.dir[0], self.dir[1],
                                   9, w["dmg"], w["acc"], w["rng"], True))

    def interact(self):
        if self.now() - self.last_interact < 250:
            return
        for res in list(self.resources):
            if math.hypot(res["x"] - self.px, res["y"] - self.py) < 34:
                self.last_interact = self.now()
                if res["kind"] == "tree":
                    if not self.tools["saw"]:
                        self.say("צריך מסור כדי לאסוף עצים - קנה בחנות!")
                        return
                    self.money += 8
                    self.say("אספת עץ! +8 כסף")
                else:
                    if not self.tools["pickaxe"]:
                        self.say("צריך מכוש כדי לכרות - קנה בחנות!")
                        return
                    self.money += 14
                    self.say("כרית מהמכרה! +14 כסף")
                self.resources.remove(res)
                return

        for crate in list(self.crates):
            if math.hypot(crate["x"] - self.px, crate["y"] - self.py) < 34:
                self.last_interact = self.now()
                self.crates.remove(crate)
                if random.random() < 0.5:
                    gain = random.randint(15, 45)
                    self.money += gain
                    self.say("פתחת תיבה! +%d כסף" % gain)
                else:
                    pid = random.choice(["small", "medium"])
                    self.potions[pid] += 1
                    self.say("פתחת תיבה ומצאת תרופה!")
                return

        if self.hp < self.max_hp:
            for pid in ("large", "medium", "small"):
                if self.potions[pid] > 0:
                    self.last_interact = self.now()
                    potion = next(p for p in POTIONS if p["id"] == pid)
                    self.potions[pid] -= 1
                    self.hp = min(self.max_hp, self.hp + potion["heal"])
                    self.say("שתית %s! +%d חיים" % (potion["name"], potion["heal"]))
                    return

    # ---------- אויבים ----------
    def update_enemies(self):
        for e in list(self.enemies):
            d = math.hypot(self.px - e.x, self.py - e.y)
            if d < 1:
                d = 1
            w = e.weapon
            if d > w["rng"] * 0.55:
                dx, dy = (self.px - e.x) / d, (self.py - e.y) / d
                speed = 1.0 + self.level * 0.03
                if self.can_move(e.x + dx * speed, e.y, e.r):
                    e.x += dx * speed
                if self.can_move(e.x, e.y + dy * speed, e.r):
                    e.y += dy * speed
            if d <= w["rng"] and self.now() - e.last_shot > w["cooldown"]:
                e.last_shot = self.now()
                dx, dy = (self.px - e.x) / d, (self.py - e.y) / d
                self.bullets.append(Bullet(e.x, e.y, dx, dy, 7, w["dmg"], w["acc"], w["rng"], False))

    # ---------- קליעים ----------
    def update_bullets(self):
        for b in self.bullets:
            nx, ny = b.x + b.dx * b.speed, b.y + b.dy * b.speed
            b.traveled += b.speed
            if self.is_wall(nx, ny) or b.traveled > b.rng:
                b.dead = True
                self.spark(nx, ny, (140, 140, 140))
                continue
            b.x, b.y = nx, ny

            if b.from_player:
                for e in self.enemies:
                    if math.hypot(b.x - e.x, b.y - e.y) < e.r + 4:
                        b.dead = True
                        if random.random() < b.acc:
                            e.hp -= random.uniform(*b.dmg)
                            self.spark(b.x, b.y, (255, 204, 51))
                            if e.hp <= 0:
                                self.enemies.remove(e)
                                gain = random.randint(20, 50)
                                self.money += gain
                                self.say("חיסלת אויב! +%d כסף" % gain)
                        else:
                            self.spark(b.x, b.y, (150, 150, 150))
                        break
            elif self.invuln <= 0 and math.hypot(b.x - self.px, b.y - self.py) < 15:
                b.dead = True
                if random.random() < b.acc:
                    self.hp -= random.uniform(*b.dmg)
                    self.spark(b.x, b.y, (255, 68, 68))
                    if self.hp <= 0:
                        self.hp = 0
                        self.game_over = True
                else:
                    self.spark(b.x, b.y, (150, 150, 150))
        self.bullets = [b for b in self.bullets if not b.dead]

    def spark(self, x, y, color):
        for _ in range(5):
            self.sparks.append([x, y, random.uniform(-3, 3), random.uniform(-3, 3), 18, color])

    def update_sparks(self):
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[4] -= 1
        self.sparks = [s for s in self.sparks if s[4] > 0]

    def check_exit(self):
        ex = self.exit_tile[0] * TILE + TILE / 2
        ey = self.exit_tile[1] * TILE + TILE / 2
        if math.hypot(self.px - ex, self.py - ey) < 22:
            self.level += 1
            self.build_level()
            self.say("סיימת את השלב! עובר לשלב %d" % self.level)

    # ---------- חנות ----------
    def shop_rows(self):
        rows = [("header", "כלים", None)]
        for t in TOOLS:
            rows.append(("tool", t, self.tools[t["id"]]))
        for cat in WEAPON_CATS:
            rows.append(("header", cat, None))
            for w in WEAPONS:
                if w["cat"] == cat:
                    rows.append(("weapon", w, w["id"] in self.owned_weapons))
        rows.append(("header", "תרופות", None))
        for p in POTIONS:
            rows.append(("potion", p, False))
        return rows

    def buy(self, kind, item):
        if kind == "tool":
            if self.tools[item["id"]] or self.money < item["price"]:
                return
            self.money -= item["price"]
            self.tools[item["id"]] = True
            self.say("קנית %s!" % item["name"])
        elif kind == "weapon":
            if item["id"] in self.owned_weapons or self.money < item["price"]:
                return
            self.money -= item["price"]
            self.owned_weapons.append(item["id"])
            self.say("קנית %s!" % item["name"])
        elif kind == "potion":
            if self.money < item["price"]:
                return
            self.money -= item["price"]
            self.potions[item["id"]] += 1
            self.say("קנית %s!" % item["name"])

    def draw_shop(self):
        panel = pygame.Rect(80, 40, SCREEN_W - 160, SCREEN_H - 80)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))
        pygame.draw.rect(self.screen, COL_PANEL, panel, border_radius=10)
        pygame.draw.rect(self.screen, COL_PANEL_LINE, panel, 2, border_radius=10)

        title = self.font_big.render(rtl("החנות"), True, (255, 204, 102))
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 10))
        sub = self.font_small.render(rtl("כסף: %d   |   גלגלת עכבר לגלילה   |   Shift לסגירה" % self.money),
                                     True, (180, 180, 180))
        self.screen.blit(sub, (panel.centerx - sub.get_width() // 2, panel.y + 54))

        self.shop_buttons = []
        y = panel.y + 84 - self.shop_scroll
        clip = pygame.Rect(panel.x + 8, panel.y + 78, panel.w - 16, panel.h - 90)
        self.screen.set_clip(clip)
        for kind, item, owned in self.shop_rows():
            if kind == "header":
                if clip.y - 30 < y < clip.bottom:
                    text = self.font.render(rtl(item), True, (255, 204, 102))
                    self.screen.blit(text, (panel.right - 24 - text.get_width(), y))
                y += 30
                continue

            row = pygame.Rect(panel.x + 24, y, panel.w - 48, 30)
            if clip.y - 30 < y < clip.bottom:
                pygame.draw.rect(self.screen, (42, 42, 48), row, border_radius=6)
                if kind == "weapon":
                    label = "%s   נזק %d-%d | דיוק %d%% | טווח %d" % (
                        item["name"], item["dmg"][0], item["dmg"][1],
                        round(item["acc"] * 100), item["rng"])
                elif kind == "tool":
                    label = "%s   %s" % (item["name"], item["desc"])
                else:
                    label = "%s   מחזירה %d חיים (יש לך %d)" % (
                        item["name"], item["heal"], self.potions[item["id"]])
                text = self.font_small.render(rtl(label), True, COL_TEXT)
                self.screen.blit(text, (row.right - 10 - text.get_width(), row.y + 7))

                btn = pygame.Rect(row.x + 8, row.y + 4, 110, 22)
                affordable = self.money >= item["price"]
                if owned:
                    color, btn_label = (85, 85, 85), "נרכש"
                elif affordable:
                    color, btn_label = (58, 125, 58), "קנה %d" % item["price"]
                else:
                    color, btn_label = (90, 60, 60), "%d כסף" % item["price"]
                pygame.draw.rect(self.screen, color, btn, border_radius=5)
                btext = self.font_small.render(rtl(btn_label), True, (255, 255, 255))
                self.screen.blit(btext, (btn.centerx - btext.get_width() // 2, btn.y + 3))
                if not owned:
                    self.shop_buttons.append((btn.copy(), kind, item))
            y += 32
        self.screen.set_clip(None)
        self.shop_max_scroll = max(0, y + self.shop_scroll - panel.bottom + 40)

    # ---------- ציור ----------
    def draw_world(self):
        world_w, world_h = self.cols * TILE, self.rows * TILE
        if world_w <= SCREEN_W:
            cam_x = -(SCREEN_W - world_w) / 2
        else:
            cam_x = max(0, min(self.px - SCREEN_W / 2, world_w - SCREEN_W))
        if world_h <= SCREEN_H:
            cam_y = -(SCREEN_H - world_h) / 2
        else:
            cam_y = max(0, min(self.py - SCREEN_H / 2, world_h - SCREEN_H))

        def sx(x):
            return int(x - cam_x)

        def sy(y):
            return int(y - cam_y)

        self.screen.fill((20, 20, 24))
        x0, x1 = int(cam_x // TILE), int((cam_x + SCREEN_W) // TILE) + 1
        y0, y1 = int(cam_y // TILE), int((cam_y + SCREEN_H) // TILE) + 1
        for gy in range(max(0, y0), min(self.rows, y1)):
            for gx in range(max(0, x0), min(self.cols, x1)):
                rect = pygame.Rect(sx(gx * TILE), sy(gy * TILE), TILE, TILE)
                if self.grid[gy][gx] == 1:
                    pygame.draw.rect(self.screen, COL_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COL_FLOOR_A if (gx + gy) % 2 == 0 else COL_FLOOR_B, rect)

        ex, ey = self.exit_tile
        pygame.draw.rect(self.screen, COL_EXIT,
                         pygame.Rect(sx(ex * TILE + 4), sy(ey * TILE + 4), TILE - 8, TILE - 8), border_radius=4)

        for res in self.resources:
            color = COL_TREE if res["kind"] == "tree" else COL_ORE
            pygame.draw.circle(self.screen, color, (sx(res["x"]), sy(res["y"])), 10)

        for crate in self.crates:
            rect = pygame.Rect(sx(crate["x"]) - 10, sy(crate["y"]) - 10, 20, 20)
            pygame.draw.rect(self.screen, COL_CRATE, rect, border_radius=3)
            pygame.draw.rect(self.screen, (90, 58, 26), rect, 2, border_radius=3)

        for e in self.enemies:
            pygame.draw.circle(self.screen, COL_ENEMY, (sx(e.x), sy(e.y)), e.r)
            self.draw_bar(sx(e.x), sy(e.y) - e.r - 10, 26, e.hp / e.max_hp, (227, 51, 51))

        color = (122, 184, 232) if self.invuln > 0 else COL_PLAYER
        pygame.draw.circle(self.screen, color, (sx(self.px), sy(self.py)), 11)
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (sx(self.px + self.dir[0] * 10), sy(self.py + self.dir[1] * 10)), 3)
        self.draw_bar(sx(self.px), sy(self.py) - 24, 30, self.hp / self.max_hp, (62, 207, 62))

        for b in self.bullets:
            pygame.draw.circle(self.screen, (255, 224, 102) if b.from_player else (255, 102, 102),
                               (sx(b.x), sy(b.y)), 3)

        for s in self.sparks:
            pygame.draw.rect(self.screen, s[5], pygame.Rect(sx(s[0]) - 2, sy(s[1]) - 2, 4, 4))

    def draw_bar(self, cx, y, w, ratio, color):
        ratio = max(0.0, min(1.0, ratio))
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(cx - w // 2 - 1, y - 1, w + 2, 7))
        pygame.draw.rect(self.screen, (55, 55, 55), pygame.Rect(cx - w // 2, y, w, 5))
        pygame.draw.rect(self.screen, color, pygame.Rect(cx - w // 2, y, int(w * ratio), 5))

    def draw_hud(self):
        bar = pygame.Rect(0, 0, SCREEN_W, 34)
        pygame.draw.rect(self.screen, (18, 18, 22), bar)
        parts = [
            "חיים: %d/%d" % (round(self.hp), self.max_hp),
            "כסף: %d" % self.money,
            "נשק: %s" % self.weapon()["name"],
            "שלב: %d" % self.level,
            "תרופות: %d" % sum(self.potions.values()),
        ]
        x = SCREEN_W - 14
        for part in parts:
            text = self.font.render(rtl(part), True, COL_TEXT)
            x -= text.get_width()
            self.screen.blit(text, (x, 7))
            x -= 26

        help_text = self.font_small.render(
            rtl("חצים = תזוזה | רווח = ירי | Ctrl = איסוף/תרופה | Shift = חנות | 1-9 = החלפת נשק"),
            True, (150, 150, 150))
        self.screen.blit(help_text, (SCREEN_W // 2 - help_text.get_width() // 2, SCREEN_H - 22))

        if self.message_timer > 0:
            self.message_timer -= 1
            text = self.font.render(rtl(self.message), True, (255, 255, 255))
            box = pygame.Rect(SCREEN_W // 2 - text.get_width() // 2 - 12, 42, text.get_width() + 24, 30)
            pygame.draw.rect(self.screen, (45, 45, 52), box, border_radius=6)
            self.screen.blit(text, (box.x + 12, box.y + 5))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        title = self.font_big.render(rtl("נגמרו החיים"), True, (230, 60, 60))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 60))
        sub = self.font.render(rtl("הגעת לשלב %d" % self.level), True, COL_TEXT)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2))
        hint = self.font.render(rtl("לחץ R כדי להתחיל מחדש"), True, (160, 220, 160))
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H // 2 + 40))

    # ---------- לולאה ראשית ----------
    def run(self):
        self.shop_buttons = []
        self.shop_max_scroll = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and not self.game_over:
                        self.shop_open = not self.shop_open
                        self.shop_scroll = 0
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        if idx < len(self.owned_weapons):
                            self.weapon_index = idx
                elif event.type == pygame.MOUSEWHEEL and self.shop_open:
                    self.shop_scroll = max(0, min(self.shop_max_scroll, self.shop_scroll - event.y * 40))
                elif event.type == pygame.MOUSEBUTTONDOWN and self.shop_open and event.button == 1:
                    for rect, kind, item in self.shop_buttons:
                        if rect.collidepoint(event.pos):
                            self.buy(kind, item)
                            break

            if not self.game_over and not self.shop_open:
                self.update_player(pygame.key.get_pressed())
                self.update_enemies()
                self.update_bullets()
                self.update_sparks()
                self.check_exit()

            self.draw_world()
            self.draw_hud()
            if self.shop_open:
                self.draw_shop()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
