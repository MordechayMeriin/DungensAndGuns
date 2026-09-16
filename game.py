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
COL_WATER = (36, 84, 148)
COL_WATER_ALT = (42, 96, 164)
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
    dict(id="saw",     name="מסור", desc="נדרש לאיסוף עצים",           price=80),
    dict(id="pickaxe", name="מכוש", desc="נדרש לכל המכרות ולהר הגעש",  price=90),
    dict(id="sickle",  name="מגל",  desc="נדרש לקציר חיטה וכותנה",     price=60),
    dict(id="rod",     name="חכה",  desc="נדרש לדוג במים עם דגים",     price=70),
    dict(id="torch",   name="לפיד", desc="נדרש כדי להיכנס למערות",     price=50),
    dict(id="boat",    name="סירה", desc="מאפשרת לעבור מעל המים",      price=150),
]
TOOL_BY_ID = {t["id"]: t for t in TOOLS}

POTIONS = [
    dict(id="small",  name="תרופה קטנה",   heal=25,  price=40),
    dict(id="medium", name="תרופה בינונית", heal=60,  price=90),
    dict(id="large",  name="תרופה גדולה",  heal=120, price=160),
]

WEAPON_BY_ID = {w["id"]: w for w in WEAPONS}

# כל סוגי המשאבים במפה. renew = אחרי כמה מילישניות המשאב חוזר (0 = נעלם לתמיד).
RESOURCE_TYPES = {
    "tree":    dict(name="עץ",          tool="saw",     value=(6, 11),   color=(58, 157, 58),   mark="עץ", renew=0,     weight=10),
    "bricks":  dict(name="מכרה לבנים",  tool="pickaxe", value=(4, 8),    color=(168, 86, 62),   mark="לב", renew=0,     weight=8),
    "copper":  dict(name="מכרה נחושת",  tool="pickaxe", value=(8, 15),   color=(205, 118, 58),  mark="נח", renew=0,     weight=8),
    "iron":    dict(name="מכרה ברזל",   tool="pickaxe", value=(12, 20),  color=(172, 176, 186), mark="בר", renew=0,     weight=7),
    "gas":     dict(name="באר גז",      tool="pickaxe", value=(20, 32),  color=(150, 112, 206), mark="גז", renew=0,     weight=5),
    "gold":    dict(name="מכרה זהב",    tool="pickaxe", value=(34, 52),  color=(228, 186, 54),  mark="זה", renew=0,     weight=4),
    "diamond": dict(name="מכרה יהלום",  tool="pickaxe", value=(60, 95),  color=(120, 226, 232), mark="יה", renew=0,     weight=2),
    "wheat":   dict(name="שדה חיטה",    tool="sickle",  value=(5, 9),    color=(222, 194, 88),  mark="חי", renew=12000, weight=8),
    "cotton":  dict(name="שדה כותנה",   tool="sickle",  value=(7, 13),   color=(238, 238, 228), mark="כו", renew=12000, weight=7),
    "cow":     dict(name="פרה",         tool=None,      value=(14, 22),  color=(206, 176, 150), mark="פר", renew=15000, weight=5),
    "sheep":   dict(name="כבשה",        tool=None,      value=(11, 18),  color=(226, 226, 214), mark="כב", renew=15000, weight=5),
    "chicken": dict(name="תרנגולת",     tool=None,      value=(7, 12),   color=(214, 120, 112), mark="תר", renew=10000, weight=6),
    "cave":    dict(name="מערה",        tool="torch",   value=(30, 80),  color=(88, 88, 104),   mark="מע", renew=0,     weight=3),
    "volcano": dict(name="הר געש רדום", tool="pickaxe", value=(60, 120), color=(196, 64, 40),   mark="הר", renew=0,     weight=2),
}
RESOURCE_KINDS = list(RESOURCE_TYPES)
RESOURCE_WEIGHTS = [RESOURCE_TYPES[k]["weight"] for k in RESOURCE_KINDS]


LATIN_RUN = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-\./+%]*(?: [A-Za-z0-9\-\./+%]+)*")
MIRRORED = {"(": ")", ")": "(", "[": "]", "]": "[", "{": "}", "}": "{", "<": ">", ">": "<"}


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
    return "".join(s if kind == "latin" else "".join(MIRRORED.get(c, c) for c in reversed(s))
                   for kind, s in reversed(parts))


def load_font(size, bold=False):
    for path in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\tahoma.ttf"):
        if os.path.exists(path):
            font = pygame.font.Font(path, size)
            font.set_bold(bold)
            return font
    return pygame.font.SysFont("arial", size, bold=bold)


# ---------- ציורים של כלי הנשק והכלים ----------
# כל ציור מצויר על לוח של 88x32 (הגובה נמדד מהמרכז: -16 למעלה, +16 למטה),
# בהגדלה של פי 4, ואז מוקטן - ככה הקווים יוצאים חלקים והנשק נראה אמיתי.

ICON_W, ICON_H, ICON_SCALE = 88, 32, 4

# תיקיית התצלומים האמיתיים. אם קובץ חסר - המשחק מצייר את הפריט בעצמו.
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
PHOTOS = {}


def load_photo(item_id):
    if item_id not in PHOTOS:
        path = os.path.join(IMAGE_DIR, "%s.png" % item_id)
        image = None
        if os.path.exists(path):
            try:
                image = pygame.image.load(path).convert_alpha()
            except pygame.error:
                image = None
        PHOTOS[item_id] = image
    return PHOTOS[item_id]


def fit_image(image, size):
    """מקטין תמונה כך שתיכנס לתיבה בלי להימתח, וממרכז אותה."""
    out = pygame.Surface(size, pygame.SRCALPHA)
    k = min(size[0] / image.get_width(), size[1] / image.get_height())
    scaled = pygame.transform.smoothscale(
        image, (max(1, int(image.get_width() * k)), max(1, int(image.get_height() * k))))
    out.blit(scaled, ((size[0] - scaled.get_width()) // 2, (size[1] - scaled.get_height()) // 2))
    return out

STEEL = (186, 190, 202)
STEEL_HI = (224, 228, 238)
STEEL_LO = (126, 130, 142)
GUNMETAL = (108, 112, 124)
BLACK = (52, 54, 60)
BLACK_HI = (76, 78, 86)
BLACK_LO = (32, 32, 38)
POLYMER = (64, 64, 72)
WOOD = (146, 96, 48)
WOOD_HI = (182, 128, 70)
WOOD_LO = (104, 66, 30)
OLIVE = (94, 104, 70)
OLIVE_HI = (124, 134, 92)
TAN = (176, 150, 96)
LENS = (118, 172, 150)


class IconPainter:
    """מצייר על לוח מוגדל, בקואורדינטות של הלוח הקטן (88x32)."""

    def __init__(self, surface, scale):
        self.surf = surface
        self.k = scale
        self.cy = surface.get_height() / 2.0

    def _pt(self, a, b):
        return (int(round(a * self.k)), int(round(self.cy + b * self.k)))

    def _len(self, v):
        return max(1, int(round(v * self.k)))

    def box(self, a, b, w, h, col, rad=0):
        rect = pygame.Rect(self._pt(a, b), (self._len(w), self._len(h)))
        pygame.draw.rect(self.surf, col, rect, border_radius=int(round(rad * self.k)))

    def poly(self, points, col):
        pygame.draw.polygon(self.surf, col, [self._pt(a, b) for a, b in points])

    def line(self, a1, b1, a2, b2, col, w=1):
        pygame.draw.line(self.surf, col, self._pt(a1, b1), self._pt(a2, b2), self._len(w))

    def circ(self, a, b, r, col, w=0):
        pygame.draw.circle(self.surf, col, self._pt(a, b), self._len(r),
                           0 if w == 0 else self._len(w))

    def arc(self, a, b, w, h, start, end, col, width=1):
        rect = pygame.Rect(self._pt(a, b), (self._len(w), self._len(h)))
        pygame.draw.arc(self.surf, col, rect, start, end, self._len(width))

    def ribs(self, a, b, count, step, height, col, w=0.7):
        for i in range(count):
            self.line(a + i * step, b, a + i * step, b + height, col, w)


def paint_glock(g):
    g.box(28, -1.6, 27, 4.2, POLYMER, 0.8)                     # מסגרת
    g.poly([(33, 2), (45.5, 2), (42, 15), (29.5, 15)], POLYMER)  # ידית
    g.poly([(34.5, 3.4), (44, 3.4), (41, 13.6), (31.5, 13.6)], (78, 78, 86))
    g.arc(39, -1.8, 13, 13, 3.35, 6.15, POLYMER, 1.4)          # מגן הדק
    g.line(44.5, 2.2, 44.5, 5.4, BLACK_LO, 1.1)                # הדק
    g.box(26, -10.6, 34, 8.6, (70, 70, 78), 0.8)               # מרעם
    g.box(26, -10.6, 34, 2.2, (92, 92, 100), 0.8)
    g.ribs(28, -9, 4, 1.7, 6, (46, 46, 52))
    g.ribs(52.5, -9, 4, 1.7, 6, (46, 46, 52))
    g.box(44, -9.6, 7.5, 3.4, (34, 34, 40), 0.4)               # חלון גילוי
    g.box(59.6, -8.6, 2.4, 4.2, STEEL_LO)                      # קנה
    g.box(27.6, -12.4, 2.8, 2, BLACK_LO)
    g.box(56, -12.4, 2.4, 2, BLACK_LO)


def paint_p226(g):
    g.box(26, -1.8, 28, 4.4, STEEL_LO, 0.8)
    g.poly([(31, 2.4), (44, 2.4), (40.5, 16), (28, 16)], (44, 42, 44))     # ידיות
    g.ribs(31, 4.5, 5, 2.2, 9, (78, 74, 76), 0.6)
    g.arc(38, -1.6, 13, 13, 3.35, 6.15, STEEL_LO, 1.4)
    g.line(43.5, 2.4, 43.5, 5.6, BLACK_LO, 1.1)
    g.box(24, -10.8, 35, 8.8, STEEL, 0.8)                                  # מרעם פלדה
    g.box(24, -10.8, 35, 2.4, STEEL_HI, 0.8)
    g.box(24, -3.4, 35, 1.4, STEEL_LO)
    g.ribs(26.5, -9, 5, 1.9, 6.4, (140, 144, 154))
    g.box(42, -9.8, 8, 3.4, (56, 56, 62), 0.4)
    g.poly([(22.5, -12.6), (26.5, -13), (26, -7), (22, -7.4)], STEEL_LO)   # נוקר
    g.box(58.6, -8.8, 2.4, 4.4, GUNMETAL)
    g.box(25.6, -12.6, 2.8, 2, BLACK_LO)
    g.box(55, -12.6, 2.4, 2, BLACK_LO)


def paint_uzi(g):
    g.line(12, -10, 28, -10, STEEL_LO, 1.3)                    # כתפייה מקופלת
    g.line(12, -10, 12, -1.5, STEEL_LO, 1.3)
    g.line(12, -1.5, 24, 1.5, STEEL_LO, 1.3)
    g.box(27, -11.4, 25, 14, BLACK, 0.8)                       # גוף מרובע
    g.box(27, -11.4, 25, 2.6, BLACK_HI, 0.8)
    g.box(32, -13.8, 11, 2.8, (98, 98, 108), 0.6)              # ידית דריכה עליונה
    g.box(50, -7, 7, 5.6, BLACK_HI, 0.6)
    g.box(56, -5.8, 8, 3, STEEL_LO)                            # קנה
    g.poly([(55, -7), (57, -12.4), (59, -7)], (110, 110, 120)) # כוונת
    g.box(29.5, -13.6, 2.6, 2.2, BLACK_LO)
    g.box(31.5, 2.2, 13.5, 6.4, BLACK_HI, 0.8)                 # ידית
    g.box(33.5, 4, 9.5, 14.5, (96, 96, 106), 0.5)              # מחסנית בתוך הידית
    g.ribs(34.5, 7, 4, 2.2, 8, (66, 66, 74), 0.6)
    g.arc(43, 1, 10, 10, 3.4, 6.1, BLACK_HI, 1.2)


def paint_mp5(g):
    g.box(4, -7.4, 18, 8.4, BLACK, 1)                          # כתפייה
    g.box(4, -7.4, 2.4, 8.4, BLACK_LO, 0.6)
    g.box(21, -10.4, 27, 11.6, BLACK_HI, 0.9)                  # גוף
    g.box(21, -10.4, 27, 2.4, (92, 94, 102), 0.9)
    g.box(28, -13.6, 19, 3.2, BLACK_HI, 1.2)                   # צינור דריכה
    g.circ(29.5, -12, 2.1, (104, 104, 114))
    g.circ(24, -13, 2.6, BLACK_HI)                             # כוונת אחורית
    g.box(47, -8.8, 15, 8.6, BLACK, 2)                         # מגן יד
    g.ribs(49, -7, 6, 2.1, 6, (40, 40, 46), 0.6)
    g.box(61, -5.8, 10, 2.8, STEEL_LO)                         # קנה
    g.circ(72, -4.4, 4.6, BLACK_HI, 1.3)                       # כוונת קדמית עגולה
    g.line(72, -8.4, 72, -5.4, BLACK_HI, 0.8)
    g.poly([(36, 2), (44.5, 2), (49.5, 15.5), (41, 16.5)], BLACK_HI)   # מחסנית
    g.poly([(24.5, 2), (33, 2), (31, 13.5), (22.5, 13.5)], BLACK)      # ידית
    g.arc(32, 1, 11, 11, 3.4, 6.1, BLACK_HI, 1.2)


def paint_m16(g):
    g.poly([(2, -8), (21, -9.2), (21, 3.4), (2, 5)], BLACK)    # קת
    g.box(2, -8, 2.4, 13, BLACK_LO, 0.6)
    g.poly([(3, -7), (20, -8.2), (20, -6.6), (3, -5.4)], BLACK_HI)
    g.box(21, -9.4, 23, 11.4, BLACK_HI, 0.8)                   # גוף
    g.box(25, -15.2, 19, 5.8, BLACK_HI, 0.8)                   # ידית נשיאה
    g.box(27, -13.8, 15, 1.6, BLACK_LO)
    g.line(26.5, -9.6, 42.5, -9.6, BLACK_LO, 0.8)
    g.box(44, -7.6, 19, 9.2, BLACK, 3)                         # מגן יד
    g.ribs(46, -6, 8, 2.1, 6.6, (38, 38, 44), 0.6)
    g.box(63, -4.2, 15, 2.8, STEEL_LO)                         # קנה
    g.poly([(65.5, -4.6), (69.5, -4.6), (68.5, -13.6), (66.5, -13.6)], BLACK_HI)  # בסיס כוונת
    g.box(66.6, -15.4, 1.8, 2, BLACK_HI)
    g.box(77.5, -5.4, 6.5, 5, BLACK_HI, 0.6)                   # בולם להבה
    g.ribs(78.5, -4.6, 3, 1.8, 3.4, BLACK_LO, 0.6)
    g.poly([(31, 3), (40, 3), (41, 16), (32, 16)], BLACK_HI)   # מחסנית
    g.poly([(23, 3), (31, 3), (29, 14), (21, 14)], BLACK)      # ידית
    g.arc(29, 2, 11, 11, 3.4, 6.1, BLACK_HI, 1.2)


def paint_ak47(g):
    g.poly([(2, -7.4), (19, -9.4), (19, 2.4), (2, 6.4)], WOOD)             # קת עץ
    g.poly([(3, -6.4), (18, -8.2), (18, -6.6), (3, -4.8)], WOOD_HI)
    g.box(19, -9.4, 22, 12.4, STEEL_LO, 0.8)                               # גוף
    g.box(21, -12, 17.5, 3, (152, 156, 166), 0.6)                          # מכסה עליון
    g.circ(24, -4, 1.1, (86, 90, 100))
    g.circ(36, -4, 1.1, (86, 90, 100))
    g.box(41, -11, 4.4, 3.2, GUNMETAL, 0.4)                                # בלוק כוונת אחורית
    g.box(45, -9.4, 15, 8.4, WOOD, 1.4)                                    # מגן יד עץ
    g.poly([(45.5, -8.6), (59.5, -8.6), (59.5, -7), (45.5, -7)], WOOD_HI)
    g.box(45, -13.2, 15, 3.6, (158, 162, 172), 0.8)                        # צינור גז
    g.box(60, -6.2, 12, 2.8, STEEL_LO)                                     # קנה
    g.poly([(68.5, -6.6), (72.5, -6.6), (71.5, -13.4), (69.5, -13.4)], GUNMETAL)
    g.box(72, -7.6, 5, 4.6, (128, 132, 142), 0.6)                          # פיית לוע
    g.poly([(29, 3), (39, 3), (46.5, 14.5), (36, 18)], (172, 112, 54))     # מחסנית מעוקלת
    g.poly([(30, 4.4), (37.6, 4.4), (43.5, 13.6), (35.5, 16)], (196, 132, 66))
    g.poly([(21, 3), (29, 3), (27, 14.5), (19, 14.5)], WOOD_LO)            # ידית
    g.arc(28, 2, 11, 11, 3.4, 6.1, STEEL_LO, 1.2)


def paint_m249(g):
    g.poly([(2, -7), (17, -9), (17, 2.4), (2, 5)], BLACK)                  # קת
    g.box(17, -11.4, 30, 16.4, BLACK_HI, 1)                                # גוף
    g.box(19, -13.8, 25, 3.2, (94, 96, 104), 0.8)                          # מכסה הזנה
    g.box(25, -16, 13, 2.6, (104, 106, 116), 0.8)                          # ידית נשיאה
    g.box(47, -8.4, 19, 6.6, (100, 102, 112), 0.8)                         # מעטה קנה
    g.ribs(49.5, -8, 6, 2.6, 6, (56, 58, 66), 0.8)
    g.box(66, -9, 7, 7, (122, 124, 134), 0.6)                              # בולם להבה
    g.box(13.5, 3.6, 19, 11.4, OLIVE, 1.4)                                 # ארגז תחמושת
    g.box(13.5, 3.6, 19, 2.6, OLIVE_HI, 1.4)
    g.poly([(31.5, 5.6), (38, 1.6), (39, 3.4), (32.5, 7.4)], TAN)          # מחסנית שרשרת
    g.line(50, 4.4, 43.5, 16, STEEL_LO, 1.4)                               # חצובה
    g.line(50, 4.4, 56.5, 16, STEEL_LO, 1.4)
    g.poly([(22, 5), (30, 5), (28, 15.5), (20, 15.5)], BLACK)              # ידית
    g.arc(29, 4, 11, 11, 3.4, 6.1, BLACK_HI, 1.2)


def paint_m2(g):
    g.box(3, -12, 4.4, 11, BLACK, 1)                                       # ידיות אחוריות
    g.box(3, 2, 4.4, 10, BLACK, 1)
    g.box(8, -9, 6, 15, BLACK_HI, 0.8)
    g.box(13, -10.4, 30, 17, BLACK_HI, 1)                                  # גוף
    g.box(13, -10.4, 30, 3, (92, 94, 102), 1)
    g.circ(20, -2, 2.2, BLACK_LO)
    g.box(43, -8.4, 36, 11.4, (96, 98, 108), 1.4)                          # מעטה קנה מחורר
    g.box(43, -8.4, 36, 2.6, (128, 130, 140), 1.4)
    for i in range(6):
        g.circ(47 + i * 5.6, -5, 1.5, (44, 44, 50))
        g.circ(47 + i * 5.6, 0, 1.5, (44, 44, 50))
    g.box(79, -5.4, 7, 5.4, (140, 142, 152), 0.6)                          # לוע
    g.line(47, 3, 36, 16, STEEL_LO, 1.5)                                   # חצובה
    g.line(47, 3, 58, 16, STEEL_LO, 1.5)
    g.line(47, 3, 47, 16, STEEL_LO, 1.5)


def paint_awp(g):
    g.poly([(2, -5), (11, -8.4), (27, -8.4), (27, 6), (13, 8.4), (2, 8.4)], OLIVE)
    g.poly([(3, -4), (12, -7), (26, -7), (26, -5.4), (3, -2.4)], OLIVE_HI)
    g.circ(13.5, 1.5, 3.2, (24, 24, 28))                                   # חור אגודל
    g.box(11, -11, 15, 3.2, OLIVE_HI, 1)                                   # משענת לחי
    g.box(26, -7, 18, 8.6, BLACK_HI, 0.8)                                  # גוף
    g.line(40, -2.4, 46, 4, STEEL, 1.8)                                    # ידית דריכה
    g.circ(46.6, 4.6, 2.1, STEEL_HI)
    g.box(26, -16.4, 26, 7.8, (42, 44, 48), 1.6)                           # טלסקופ
    g.box(26, -16.4, 26, 2.2, (66, 68, 74), 1.6)
    g.box(24.2, -15.4, 2.4, 6, LENS, 0.4)
    g.box(51.4, -15.4, 5.6, 6.2, (42, 44, 48), 0.8)                        # מצחיית עדשה
    g.box(56, -14.6, 1.8, 4.6, LENS, 0.4)
    g.box(29.5, -9.2, 3.2, 3, (58, 58, 64))
    g.box(45, -9.2, 3.2, 3, (58, 58, 64))
    g.box(30, 1.6, 9, 4.4, BLACK_HI, 0.5)                                  # מחסנית
    g.box(44, -4.4, 31, 4.2, (104, 106, 116))                              # קנה
    g.ribs(50, -3.6, 6, 3.4, 2.6, (78, 80, 90), 0.6)
    g.box(74, -5.4, 8, 6.2, (84, 86, 94), 0.6)                             # בולם
    g.line(63, 0, 57, 14.5, STEEL_LO, 1.4)                                 # חצובה
    g.line(63, 0, 69, 14.5, STEEL_LO, 1.4)


def paint_barrett(g):
    g.poly([(2, -6), (13, -8), (13, 4.4), (2, 9)], BLACK)                  # קת
    g.box(11, -8.4, 55, 12.4, BLACK_HI, 1)                                 # גוף ארוך
    g.box(11, -8.4, 55, 2.6, (92, 94, 102), 1)
    g.circ(20, -1, 2.4, BLACK_LO)
    g.circ(27, -1, 2.4, BLACK_LO)
    g.box(24, -17, 29, 8.4, (42, 44, 48), 1.6)                             # טלסקופ גדול
    g.box(24, -17, 29, 2.4, (66, 68, 74), 1.6)
    g.box(22.2, -16, 2.4, 6.4, LENS, 0.4)
    g.box(52.4, -16, 2.4, 6.4, LENS, 0.4)
    g.box(27, -9.4, 3.4, 3.2, (58, 58, 64))
    g.box(47, -9.4, 3.4, 3.2, (58, 58, 64))
    g.box(65, -5.4, 11, 6.4, (108, 110, 120))                              # קנה
    g.box(75, -8.6, 11, 12.6, (88, 90, 98), 0.8)                           # בולם להבה גדול
    g.box(77.5, -6.4, 2.2, 8, BLACK_LO)
    g.box(81.5, -6.4, 2.2, 8, BLACK_LO)
    g.poly([(25, 4), (33, 4), (31, 15.5), (23, 15.5)], BLACK)              # ידית
    g.arc(31, 3, 11, 11, 3.4, 6.1, BLACK_HI, 1.2)
    g.line(58, 4, 52, 16, STEEL_LO, 1.4)                                   # חצובה
    g.line(58, 4, 64, 16, STEEL_LO, 1.4)


WEAPON_PAINTERS = {
    "glock": paint_glock, "p226": paint_p226, "uzi": paint_uzi, "mp5": paint_mp5,
    "m16": paint_m16, "ak47": paint_ak47, "m249": paint_m249, "m2": paint_m2,
    "awp": paint_awp, "barrett": paint_barrett,
}


def paint_saw(g):
    g.box(3, -11.5, 16, 17, WOOD, 4)                                       # ידית עץ
    g.box(3, -11.5, 16, 4, WOOD_HI, 4)
    g.circ(10.5, -3, 3.4, (24, 24, 28))
    g.circ(6.5, -8, 1, WOOD_LO)
    g.poly([(17, -9.5), (77, -6), (77, 2), (17, 5.5)], STEEL)              # להב
    g.poly([(18, -8.4), (76, -5), (76, -3), (18, -6.4)], STEEL_HI)
    for i in range(13):
        a = 19 + i * 4.5
        g.poly([(a, 4.6), (a + 4.5, 4.4), (a + 2.2, 9.5)], STEEL)          # שיניים
    g.circ(13, -9, 1.2, (60, 60, 66))


def paint_pickaxe(g):
    g.poly([(41, -6), (47, -6), (49, 16), (39, 16)], WOOD)                 # ידית
    g.poly([(42, -5), (44.5, -5), (45.5, 15), (42.5, 15)], WOOD_HI)
    g.poly([(15, -15.5), (30, -11), (44, -8.6), (58, -11), (73, -15.5),
            (70, -10.5), (57, -6.5), (44, -4.6), (31, -6.5), (18, -10.5)], STEEL_LO)
    g.poly([(18, -13.4), (31, -9.4), (44, -7.2), (57, -9.4), (69, -13.2),
            (67, -11.6), (56, -8.2), (44, -6.2), (32, -8.2), (20, -11.6)], STEEL_HI)
    g.box(40, -10.5, 8.5, 6.5, (152, 156, 166), 1)                         # עין המכוש


def paint_sickle(g):
    g.poly([(8, 15), (14, 8.5), (22, 12), (16, 17)], WOOD)                 # ידית
    g.poly([(9, 13.6), (14.5, 9.4), (17.5, 10.6), (12, 15)], WOOD_HI)
    g.arc(15, -13, 52, 34, 0.35, 3.4, STEEL, 3.2)                          # להב מעוקל
    g.arc(18, -10, 46, 29, 0.5, 3.35, STEEL_HI, 1.1)


def paint_rod(g):
    g.box(0, 13.5, 88, 3, (48, 88, 146))                                   # מים
    g.line(0, 13.8, 88, 13.8, (78, 126, 190), 0.8)
    g.poly([(7, 10.5), (10.5, 7.5), (62, -14), (60, -16)], WOOD)           # קנה
    g.circ(17, 5.5, 4.2, (58, 58, 66))                                     # גלגלת
    g.circ(17, 5.5, 2, (150, 152, 162))
    g.line(17, 5.5, 13, 9, (58, 58, 66), 1.2)
    g.circ(33, -1.5, 1.4, (150, 152, 162), 0.6)
    g.circ(48, -8, 1.2, (150, 152, 162), 0.6)
    g.line(61, -15, 66, 0, (226, 228, 238), 0.6)                           # חוט
    g.line(66, 0, 67, 8, (226, 228, 238), 0.6)
    g.circ(67, 10, 3.6, (226, 76, 76))                                     # מצוף
    g.box(63.4, 10, 7.2, 3.6, (238, 238, 244))
    g.arc(70, 4, 8, 8, 3.3, 6.0, STEEL, 1)                                 # קרס


def paint_torch(g):
    g.poly([(13, 17), (18, 14.5), (41, 1), (37, -2.5)], WOOD)              # מקל
    g.poly([(14, 15.6), (17, 14), (39, 1), (37.6, -0.6)], WOOD_HI)
    g.poly([(36, 1.5), (33, -4), (37, -6)], (120, 96, 60))                 # בד
    g.poly([(40, 3), (32, -4.5), (38.5, -8), (43, -18), (50, -8.5),
            (53, -0.5), (46.5, 5)], (238, 126, 34))                        # להבה
    g.poly([(41, 1.5), (37, -4), (42, -8), (45, -14), (48.5, -7),
            (49.5, -1), (45, 3)], (250, 178, 56))
    g.poly([(42.5, 0), (40.5, -5), (44, -10), (46.5, -5), (46, 0.5)], (252, 230, 130))


def paint_boat(g):
    g.box(0, 11, 88, 5, (48, 88, 146))                                     # מים
    g.line(0, 11.4, 88, 11.4, (82, 130, 194), 0.9)
    g.line(44, 1, 44, -15, WOOD_LO, 1.2)                                   # תורן
    g.poly([(46, -14), (62, -1.5), (46, -1.5)], (240, 240, 246))           # מפרש
    g.poly([(47.5, -11), (57, -3), (47.5, -3)], (216, 218, 228))
    g.poly([(11, 0.5), (77, 0.5), (68, 11), (20, 11)], WOOD)               # גוף הסירה
    g.poly([(12, 1.5), (76, 1.5), (74, 3.6), (14, 3.6)], WOOD_HI)
    g.line(22, 6, 66, 6, WOOD_LO, 0.8)
    g.poly([(11, -1), (77, -1), (77, 1), (11, 1)], (168, 116, 62))         # דופן עליונה
    g.poly([(24, 3), (30, 3), (30, 8), (24, 8)], WOOD_LO)                  # ספסל


TOOL_PAINTERS = {
    "saw": paint_saw, "pickaxe": paint_pickaxe, "sickle": paint_sickle,
    "rod": paint_rod, "torch": paint_torch, "boat": paint_boat,
}


def paint_potion(g, size):
    w = 15 + size * 6
    h = 15 + size * 5
    left = 44 - w / 2.0
    top = 13 - h
    g.box(left + w / 2 - 3.4, top - 6.5, 6.8, 7, (206, 210, 220), 0.5)     # צוואר
    g.box(left + w / 2 - 5, top - 11, 10, 5.5, (158, 112, 64), 1.4)        # פקק
    g.box(left, top, w, h, (222, 230, 242), 3)                             # זכוכית
    g.box(left + 1.6, top + h * 0.34, w - 3.2, h * 0.66 - 1.6, (216, 58, 70), 2.4)
    g.box(left + 2.4, top + 2, 2.4, h - 5, (250, 252, 255), 1)             # ברק
    cx, ccy = left + w / 2.0, top + h * 0.68                                # צלב לבן
    g.box(cx - 1.6, ccy - 4.6, 3.2, 9.2, (255, 255, 255))
    g.box(cx - 4.6, ccy - 1.6, 9.2, 3.2, (255, 255, 255))


def build_icon(kind, item, size):
    """מחזיר תצלום אמיתי של הפריט אם יש, ואחרת מצייר אותו."""
    photo = load_photo(item["id"])
    if photo is not None:
        return fit_image(photo, size)
    work = pygame.Surface((ICON_W * ICON_SCALE, ICON_H * ICON_SCALE), pygame.SRCALPHA)
    painter = IconPainter(work, ICON_SCALE)
    if kind == "weapon":
        WEAPON_PAINTERS[item["id"]](painter)
    elif kind == "tool":
        TOOL_PAINTERS[item["id"]](painter)
    else:
        paint_potion(painter, {"small": 0, "medium": 1, "large": 2}[item["id"]])
    return pygame.transform.smoothscale(work, size)


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
        self.icon_cache = {}
        self.reset_game()

    # ---------- מצב המשחק ----------
    def reset_game(self):
        self.level = 1
        self.hp = 100
        self.max_hp = 100
        self.money = 100
        self.owned_weapons = ["glock"]
        self.weapon_index = 0
        self.tools = {t["id"]: False for t in TOOLS}
        self.potions = {"small": 0, "medium": 0, "large": 0}
        self.game_over = False
        self.shop_open = False
        self.shop_scroll = 0
        self.message = ""
        self.message_timer = 0
        self.last_shot = 0
        self.last_interact = 0
        self.inspect = None
        self.inspect_until = 0
        self.cam_x = 0.0
        self.cam_y = 0.0
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

        self.max_weapon = min(3 + self.level // 2, len(WEAPONS))
        self.enemies = []
        for (tx, ty) in take(min(3 + self.level, 12)):
            self.enemies.append(self.make_enemy(tx * TILE + TILE / 2, ty * TILE + TILE / 2))

        self.resources = []
        for (tx, ty) in take(9 + self.level * 2):
            kind = random.choices(RESOURCE_KINDS, weights=RESOURCE_WEIGHTS)[0]
            self.resources.append(dict(x=tx * TILE + TILE / 2, y=ty * TILE + TILE / 2,
                                       kind=kind, ready_at=0))

        self.crates = [dict(x=tx * TILE + TILE / 2, y=ty * TILE + TILE / 2)
                       for (tx, ty) in take(3 + self.level // 2)]

        self.fish_cooldown = {}
        self.inspect = None
        self.place_water(free)

        self.bullets = []
        self.sparks = []

    def make_enemy(self, x, y):
        weapon = WEAPONS[random.randrange(self.max_weapon)]
        return Enemy(x, y, weapon, 30 + self.level * 6)

    def place_water(self, candidates):
        """פורס שלוליות מים, אבל תמיד משאיר דרך יבשה מההתחלה ליציאה."""
        random.shuffle(candidates)
        placed = 0
        target = 5 + self.level * 2
        for (x, y) in candidates:
            if placed >= target:
                break
            self.grid[y][x] = 2
            if self.path_exists((1, 1), self.exit_tile):
                placed += 1
            else:
                self.grid[y][x] = 0
        water = [(x, y) for y in range(self.rows) for x in range(self.cols)
                 if self.grid[y][x] == 2]
        random.shuffle(water)
        for (x, y) in water[:max(1, len(water) // 3)]:
            self.grid[y][x] = 3

    def path_exists(self, start, goal):
        seen = {start}
        queue = [start]
        while queue:
            x, y = queue.pop()
            if (x, y) == goal:
                return True
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (0 <= nx < self.cols and 0 <= ny < self.rows
                        and (nx, ny) not in seen and self.grid[ny][nx] == 0):
                    seen.add((nx, ny))
                    queue.append((nx, ny))
        return False

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

    def tile_at(self, px, py):
        gx, gy = int(px // TILE), int(py // TILE)
        if gx < 0 or gy < 0 or gx >= self.cols or gy >= self.rows:
            return 1
        return self.grid[gy][gx]

    def is_wall(self, px, py):
        return self.tile_at(px, py) == 1

    def blocked(self, px, py, boat):
        tile = self.tile_at(px, py)
        return tile == 1 or (tile in (2, 3) and not boat)

    def can_move(self, x, y, r, boat=False):
        return not (self.blocked(x - r, y - r, boat) or self.blocked(x + r, y - r, boat) or
                    self.blocked(x - r, y + r, boat) or self.blocked(x + r, y + r, boat))

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
            boat = self.tools["boat"]
            if self.can_move(self.px + dx * speed, self.py, 11, boat):
                self.px += dx * speed
            if self.can_move(self.px, self.py + dy * speed, 11, boat):
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

    def nearest_resource(self):
        best, best_d = None, 36
        for res in self.resources:
            d = math.hypot(res["x"] - self.px, res["y"] - self.py)
            if d < best_d:
                best, best_d = res, d
        return best

    def nearest_fish_tile(self):
        """מחפש אריח מים עם דגים ליד השחקן (אפשר לדוג גם מהחוף)."""
        gx, gy = int(self.px // TILE), int(self.py // TILE)
        best, best_d = None, 1.7
        for ty in range(gy - 1, gy + 2):
            for tx in range(gx - 1, gx + 2):
                if 0 <= tx < self.cols and 0 <= ty < self.rows and self.grid[ty][tx] == 3:
                    d = math.hypot(tx + 0.5 - self.px / TILE, ty + 0.5 - self.py / TILE)
                    if d < best_d:
                        best, best_d = (tx, ty), d
        return best

    def interact(self):
        if self.now() - self.last_interact < 250:
            return

        if self.at_exit():
            self.last_interact = self.now()
            self.leave_level()
            return

        res = self.nearest_resource()
        if res is not None:
            self.last_interact = self.now()
            self.harvest(res)
            return

        tile = self.nearest_fish_tile()
        if tile is not None:
            self.last_interact = self.now()
            self.go_fishing(tile)
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

    def harvest(self, res):
        info = RESOURCE_TYPES[res["kind"]]
        tool = info["tool"]
        if tool and not self.tools[tool]:
            self.say("צריך %s בשביל %s - קנה בחנות!" % (TOOL_BY_ID[tool]["name"], info["name"]))
            return
        if res["ready_at"] > self.now():
            self.say("%s עוד לא מוכן - חכה קצת" % info["name"])
            return

        gain = random.randint(*info["value"])
        self.money += gain

        if res["kind"] == "cave":
            extra = ""
            if random.random() < 0.4:
                pid = random.choice(["small", "medium", "large"])
                self.potions[pid] += 1
                extra = " ומצאת תרופה"
            self.say("חקרת את המערה! +%d כסף%s" % (gain, extra))
            if random.random() < 0.35:
                self.enemies.append(self.make_enemy(res["x"], res["y"]))
                self.say("יצא אויב מהמערה! היזהר")
        elif res["kind"] == "volcano":
            if random.random() < 0.3:
                self.hp -= 10
                if self.hp <= 0:
                    self.hp = 0
                    self.game_over = True
                self.say("כרית בהר הגעש! +%d כסף אבל נכווית (-10 חיים)" % gain)
            else:
                self.say("כרית אבן געש! +%d כסף" % gain)
        else:
            self.say("אספת %s! +%d כסף" % (info["name"], gain))

        if info["renew"]:
            res["ready_at"] = self.now() + info["renew"]
        else:
            self.resources.remove(res)

    def go_fishing(self, tile):
        if not self.tools["rod"]:
            self.say("צריך חכה כדי לדוג - קנה בחנות!")
            return
        if self.fish_cooldown.get(tile, 0) > self.now():
            self.say("אין כאן דגים כרגע - חכה קצת")
            return
        gain = random.randint(9, 16)
        self.money += gain
        self.fish_cooldown[tile] = self.now() + 9000
        self.say("דגת דג! +%d כסף" % gain)

    def interact_hint(self):
        """שורת עזרה קטנה שמראה מה אפשר לעשות במקום שבו אתה עומד."""
        if self.at_exit():
            return "Ctrl = מעבר לשלב הבא"
        res = self.nearest_resource()
        if res is not None:
            info = RESOURCE_TYPES[res["kind"]]
            tool = info["tool"]
            if tool and not self.tools[tool]:
                return "%s - צריך %s" % (info["name"], TOOL_BY_ID[tool]["name"])
            if res["ready_at"] > self.now():
                return "%s - עוד לא מוכן" % info["name"]
            return "Ctrl = %s" % info["name"]
        tile = self.nearest_fish_tile()
        if tile is not None:
            if not self.tools["rod"]:
                return "מים עם דגים - צריך חכה"
            if self.fish_cooldown.get(tile, 0) > self.now():
                return "מים עם דגים - עוד לא חזרו"
            return "Ctrl = דיג"
        for crate in self.crates:
            if math.hypot(crate["x"] - self.px, crate["y"] - self.py) < 34:
                return "Ctrl = פתיחת תיבה"
        return ""

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

    def at_exit(self):
        ex = self.exit_tile[0] * TILE + TILE / 2
        ey = self.exit_tile[1] * TILE + TILE / 2
        return math.hypot(self.px - ex, self.py - ey) < 24

    def leave_level(self):
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
                if clip.y - 46 < y < clip.bottom:
                    text = self.font.render(rtl(item), True, (255, 204, 102))
                    self.screen.blit(text, (panel.right - 24 - text.get_width(), y))
                y += 30
                continue

            row = pygame.Rect(panel.x + 24, y, panel.w - 48, 46)
            if clip.y - 46 < y < clip.bottom:
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
                self.screen.blit(text, (row.right - 10 - text.get_width(), row.y + 15))

                btn = pygame.Rect(row.x + 8, row.y + 12, 110, 22)
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
                self.draw_item_icon(pygame.Rect(btn.right + 12, row.y + 3, 110, 40), kind, item)
                if not owned:
                    self.shop_buttons.append((btn.copy(), kind, item))
            y += 48
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

        self.cam_x, self.cam_y = cam_x, cam_y

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
                tile = self.grid[gy][gx]
                if tile == 1:
                    pygame.draw.rect(self.screen, COL_WALL, rect)
                elif tile in (2, 3):
                    pygame.draw.rect(self.screen, COL_WATER if (gx + gy) % 2 == 0 else COL_WATER_ALT, rect)
                    pygame.draw.line(self.screen, (70, 130, 200),
                                     (rect.x + 5, rect.y + 7), (rect.x + TILE - 6, rect.y + 7))
                    if tile == 3:
                        ready = self.fish_cooldown.get((gx, gy), 0) <= self.now()
                        fish_col = (240, 176, 72) if ready else (74, 110, 150)
                        pygame.draw.ellipse(self.screen, fish_col,
                                            pygame.Rect(rect.x + 10, rect.y + 16, 13, 8))
                        pygame.draw.polygon(self.screen, fish_col,
                                            [(rect.x + 10, rect.y + 20), (rect.x + 4, rect.y + 15),
                                             (rect.x + 4, rect.y + 25)])
                else:
                    pygame.draw.rect(self.screen, COL_FLOOR_A if (gx + gy) % 2 == 0 else COL_FLOOR_B, rect)

        ex, ey = self.exit_tile
        gate = pygame.Rect(sx(ex * TILE + 2), sy(ey * TILE + 2), TILE - 4, TILE - 4)
        pygame.draw.rect(self.screen, (62, 52, 20), gate, border_radius=4)          # פתח פתוח
        pygame.draw.rect(self.screen, COL_EXIT, gate, 3, border_radius=4)           # מסגרת
        bright = math.sin(self.now() / 260.0) > 0
        arrow = (255, 236, 140) if bright else COL_EXIT
        acx, acy = gate.centerx, gate.centery
        pygame.draw.polygon(self.screen, arrow,
                            [(acx, acy - 9), (acx - 8, acy - 1), (acx - 3, acy - 1),
                             (acx - 3, acy + 8), (acx + 3, acy + 8), (acx + 3, acy - 1),
                             (acx + 8, acy - 1)])

        for res in self.resources:
            info = RESOURCE_TYPES[res["kind"]]
            ready = res["ready_at"] <= self.now()
            color = info["color"] if ready else tuple(c // 2 for c in info["color"])
            cx, cy = sx(res["x"]), sy(res["y"])
            pygame.draw.circle(self.screen, color, (cx, cy), 13)
            pygame.draw.circle(self.screen, (16, 16, 20), (cx, cy), 13, 1)
            text_col = (20, 20, 24) if sum(color) > 420 else (245, 245, 245)
            mark = self.font_small.render(rtl(info["mark"]), True, text_col)
            self.screen.blit(mark, (cx - mark.get_width() // 2, cy - mark.get_height() // 2))

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

    # ---------- ציורים של הנשקים והכלים ----------
    def icon_surface(self, kind, item, size):
        key = (kind, item["id"], size)
        if key not in self.icon_cache:
            self.icon_cache[key] = build_icon(kind, item, size)
        return self.icon_cache[key]

    def draw_item_icon(self, rect, kind, item):
        pygame.draw.rect(self.screen, (24, 24, 28), rect, border_radius=4)
        self.screen.blit(self.icon_surface(kind, item, (rect.w, rect.h)), rect.topleft)

    def draw_weapon_icon(self, rect, weapon):
        self.draw_item_icon(rect, "weapon", weapon)

    def inspect_enemy_at(self, pos):
        """לחיצת עכבר על אויב - מראה איזה נשק יש לו."""
        wx, wy = pos[0] + self.cam_x, pos[1] + self.cam_y
        for e in self.enemies:
            if math.hypot(wx - e.x, wy - e.y) <= e.r + 8:
                self.inspect = e
                self.inspect_until = self.now() + 5000
                return
        self.inspect = None

    def draw_inspect(self):
        e = self.inspect
        if e is None or e not in self.enemies or self.inspect_until < self.now():
            return
        w = e.weapon
        lines = [
            self.font_small.render(rtl("%s - %s" % (w["name"], w["cat"])), True, (255, 226, 150)),
            self.font_small.render(rtl("נזק %d-%d | דיוק %d%% | טווח %d" % (
                w["dmg"][0], w["dmg"][1], round(w["acc"] * 100), w["rng"])), True, COL_TEXT),
            self.font_small.render(rtl("חיים: %d/%d" % (round(e.hp), e.max_hp)), True, (255, 168, 168)),
        ]
        width = max(t.get_width() for t in lines) + 110 + 30
        height = 76
        bx = int(e.x - self.cam_x) - width // 2
        by = int(e.y - self.cam_y) - e.r - height - 10
        bx = max(6, min(SCREEN_W - width - 6, bx))
        by = max(40, by)
        box = pygame.Rect(bx, by, width, height)
        pygame.draw.rect(self.screen, (26, 26, 32), box, border_radius=7)
        pygame.draw.rect(self.screen, (198, 92, 92), box, 2, border_radius=7)
        self.draw_weapon_icon(pygame.Rect(box.x + 10, box.y + 18, 110, 40), w)
        for i, text in enumerate(lines):
            self.screen.blit(text, (box.right - 10 - text.get_width(), box.y + 12 + i * 17))

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

        hint = self.interact_hint()
        if hint:
            text = self.font.render(rtl(hint), True, (255, 226, 150))
            box = pygame.Rect(SCREEN_W // 2 - text.get_width() // 2 - 12, SCREEN_H - 62,
                              text.get_width() + 24, 30)
            pygame.draw.rect(self.screen, (44, 44, 52), box, border_radius=6)
            pygame.draw.rect(self.screen, (110, 100, 70), box, 1, border_radius=6)
            self.screen.blit(text, (box.x + 12, box.y + 5))

        help_text = self.font_small.render(
            rtl("חצים = תזוזה | רווח = ירי | Ctrl = איסוף/תרופה/סיום שלב | Shift = חנות | 1-9 = נשק | קליק על אויב = הנשק שלו"),
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
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.shop_open:
                        for rect, kind, item in self.shop_buttons:
                            if rect.collidepoint(event.pos):
                                self.buy(kind, item)
                                break
                    elif not self.game_over:
                        self.inspect_enemy_at(event.pos)

            if not self.game_over and not self.shop_open:
                self.update_player(pygame.key.get_pressed())
                self.update_enemies()
                self.update_bullets()
                self.update_sparks()

            self.draw_world()
            self.draw_inspect()
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
