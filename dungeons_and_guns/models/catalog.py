# -*- coding: utf-8 -*-
"""הגדרות של פריטים קבועים: נשק, תחמושת, ציוד, כלים, תרופות, אוכל, משאבים וגלגל המזל.

All catalog models are frozen: they describe *what an item is*, never what the player has.
"""

from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from .enums import GearCategory, ItemKind, ResourceKind, WeaponCategory, WeaponKind, WheelOutcome


# איזו תחמושת צורך כל נשק חם, לפי המחלקה שלו (אפשר לדרוס לכל נשק בנפרד)
DEFAULT_AMMO: dict[WeaponCategory, str] = {
    WeaponCategory.PISTOLS: "ammo_pistol",
    WeaponCategory.SMGS: "ammo_smg",
    WeaponCategory.RIFLES: "ammo_rifle",
    WeaponCategory.SHOTGUNS: "ammo_shell",
    WeaponCategory.SNIPERS: "ammo_sniper",
    WeaponCategory.HEAVY: "ammo_mg",
}


def _check_range(value: tuple[int, int]) -> tuple[int, int]:
    low, high = value
    if low > high:
        raise ValueError("range %r: low is greater than high" % (value,))
    return value


Color = tuple[int, int, int]
Range = Annotated[tuple[int, int], AfterValidator(_check_range)]   # (מינימום, מקסימום)


class ItemBase(BaseModel):
    """כל דבר שאפשר לקנות בחנות."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    price: int = Field(ge=0)
    art: str = ""           # איזה ציור להשתמש בו כשאין תצלום אמיתי (ברירת מחדל: ה-id)
    desc: str = ""

    @model_validator(mode="before")
    @classmethod
    def _default_art(cls, data: Any) -> Any:
        if isinstance(data, dict) and not data.get("art"):
            data = {**data, "art": data.get("id", "")}
        return data


class Weapon(ItemBase):
    cat: WeaponCategory
    kind: WeaponKind
    dmg: Range
    acc: float = Field(ge=0, le=1)
    rng: int = Field(gt=0)
    cooldown: int = Field(ge=0)
    speed: float = 9            # מהירות הקליע
    pellets: int = Field(1, ge=1)
    radius: int = 0             # רדיוס הפיצוץ, לרימונים
    ammo: str | None = None     # סוג התחמושת; נקבע לפי המחלקה אם לא כתוב
    wall_power: int = Field(0, ge=0, le=2)  # לבני חבלה: 1 = שובר קיר רגיל, 2 = גם משוריין

    @model_validator(mode="before")
    @classmethod
    def _default_ammo(cls, data: Any) -> Any:
        if isinstance(data, dict) and "ammo" not in data and data.get("kind") == WeaponKind.GUN:
            data = {**data, "ammo": DEFAULT_AMMO.get(WeaponCategory(data["cat"]))}
        return data

    @property
    def is_throwable(self) -> bool:
        """רימונים ולבני חבלה: נקנים ונספרים ביחידות, וכל אחד נגמר כשמשתמשים בו."""
        return self.kind in (WeaponKind.THROW, WeaponKind.PLACE)


class Gear(ItemBase):
    """ציוד שנקנה פעם אחת ועובד לבד (הגנה) או משפר את הנשק."""

    cat: GearCategory
    reduce: float = 0.0     # כמה נזק נחסם
    slow: float = 0.0       # כמה התנועה מואטת
    acc: float = 0.0        # תוספת דיוק
    rng: float = 0.0        # תוספת טווח (יחסית)


class AmmoType(ItemBase):
    pack: int = Field(gt=0)
    unit: str = "כדורים"


class Tool(ItemBase):
    pass


class Key(ItemBase):
    """מפתח - פותח שער אחד ונעלם."""


class Potion(ItemBase):
    heal: int = Field(gt=0)


class Food(ItemBase):
    """אוכל - מכינים בסדנה או דגים, ואוכלים (F או משורת המספרים). לא נמכר בחנות."""

    price: int = 0
    heal: int = Field(gt=0)


class WheelTicket(ItemBase):
    """סיבוב בגלגל המזל, כפי שהוא מופיע בחנות."""


class WheelSlice(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: WheelOutcome
    name: str
    color: Color
    good: bool


class Rank(BaseModel):
    """דרגה: מכמה נקודות מקבלים אותה, ואילו כלי נשק היא פותחת בחנות."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    points: int = Field(ge=0)
    unlocks: tuple[str, ...] = ()   # ה-id של כלי הנשק שנפתחים בדרגה הזו


class ResourceType(BaseModel):
    """סוג משאב במפה. renew = אחרי כמה מילישניות המשאב חוזר (0 = נעלם לתמיד)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: ResourceKind
    name: str
    material: str | None = None     # הפריט שנכנס לתיק בכל איסוף (למשל "מטיל ברזל")
    tool: str | None
    value: Range
    color: Color
    mark: str
    renew: int = 0
    weight: int = Field(gt=0)


def _check_needs(value: dict[ResourceKind, int]) -> dict[ResourceKind, int]:
    if not value or any(n <= 0 for n in value.values()):
        raise ValueError("a recipe needs at least one material, each at least once")
    return value


class Recipe(BaseModel):
    """מתכון בסדנה: מה מכינים, ואילו חומרים מהתיק זה עולה."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: ItemKind
    item: str                   # ה-id של הפריט שמקבלים
    needs: Annotated[dict[ResourceKind, int], AfterValidator(_check_needs)]
