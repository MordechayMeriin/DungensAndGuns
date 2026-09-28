# -*- coding: utf-8 -*-
"""צבעים של המסך."""

WALL = (58, 58, 68)
ARMORED = (78, 86, 100)         # קיר משוריין
ARMORED_EDGE = (132, 142, 160)
GATE = (150, 104, 44)           # שער נעול
FLOOR_A = (35, 35, 40)
FLOOR_B = (38, 38, 44)
PLAYER = (59, 120, 194)
ENEMY = (194, 59, 59)
EXIT = (232, 197, 58)
CRATE = (138, 90, 42)
WATER = (36, 84, 148)
WATER_ALT = (42, 96, 164)
TEXT = (235, 235, 235)
PANEL = (30, 30, 34)
PANEL_LINE = (100, 100, 110)
GOLD = (255, 214, 102)

# מד החיים מחליף צבע כל 25 אחוז: ירוק, צהוב, כתום, אדום
HP_GREEN = (62, 207, 62)
HP_YELLOW = (226, 214, 62)
HP_ORANGE = (234, 148, 46)
HP_RED = (226, 56, 56)


def hp_color(ratio: float) -> tuple[int, int, int]:
    """ירוק מעל 75%, צהוב מעל 50%, כתום מעל 25%, ואדום מתחת."""
    if ratio > 0.75:
        return HP_GREEN
    if ratio > 0.5:
        return HP_YELLOW
    if ratio > 0.25:
        return HP_ORANGE
    return HP_RED
