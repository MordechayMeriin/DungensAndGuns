# -*- coding: utf-8 -*-
"""קבועים עם שם: סוגי אריחים, סוגי נשק, מחלקות וכו'.

Category values are the Hebrew names shown in the shop, so the enum doubles as display text.
"""

from enum import IntEnum, StrEnum


class Tile(IntEnum):
    FLOOR = 0
    WALL = 1
    WATER = 2
    FISH = 3        # מים עם דגים

    @property
    def is_water(self) -> bool:
        return self in (Tile.WATER, Tile.FISH)


class WeaponKind(StrEnum):
    GUN = "gun"         # יורה קליעים
    MELEE = "melee"     # מכה מקרוב
    THROW = "throw"     # זריקת רימון


class WeaponCategory(StrEnum):
    PISTOLS = "אקדחים"
    SHOTGUNS = "רובי צייד"
    SMGS = "תתי מקלע"
    RIFLES = "רובי סער"
    SNIPERS = "רובי צלפים"
    HEAVY = "מקלעים כבדים"
    COLD = "נשק קר"
    GRENADES = "רימונים"


class GearCategory(StrEnum):
    PROTECTION = "הגנה"
    UPGRADES = "שיפורי נשק"


class ResourceKind(StrEnum):
    TREE = "tree"
    BRICKS = "bricks"
    COPPER = "copper"
    IRON = "iron"
    GAS = "gas"
    GOLD = "gold"
    DIAMOND = "diamond"
    WHEAT = "wheat"
    COTTON = "cotton"
    COW = "cow"
    SHEEP = "sheep"
    CHICKEN = "chicken"
    CAVE = "cave"
    VOLCANO = "volcano"


class CrateKind(StrEnum):
    GOOD = "good"
    BAD = "bad"
    EMPTY = "empty"


class WheelOutcome(StrEnum):
    MONEY = "money"
    SICK = "sick"
    POTION = "potion"
    LOSE_MONEY = "lose_money"
    GRENADES = "grenades"
    WEAPON = "weapon"
    LOSE_HP = "lose_hp"
    TOOL = "tool"
    GEAR = "gear"
    HEAL = "heal"
