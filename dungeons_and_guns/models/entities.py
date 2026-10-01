# -*- coding: utf-8 -*-
"""דברים שחיים בתוך המבוך: אויבים, קליעים, רימונים, עשן, ניצוצות, משאבים ותיבות."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .catalog import Color, Range, Weapon
from .enums import CrateKind, ResourceKind

_next_uid = 1


def _new_uid() -> int:
    global _next_uid
    uid, _next_uid = _next_uid, _next_uid + 1
    return uid


class Entity(BaseModel):
    """משהו עם מיקום במבוך.

    Every entity gets a unique ``uid`` so two entities with identical fields are still
    different objects for ``==`` / ``list.remove`` / ``in``.
    """

    model_config = ConfigDict(extra="forbid")

    uid: int = Field(default_factory=_new_uid)
    x: float
    y: float

    @model_validator(mode="after")
    def _reserve_uid(self) -> "Entity":
        # אחרי טעינת משחק שמור - אויבים חדשים יקבלו מספר שעוד לא תפוס
        global _next_uid
        _next_uid = max(_next_uid, self.uid + 1)
        return self


class Enemy(Entity):
    weapon: Weapon
    hp: float
    max_hp: float
    r: int = 12
    last_shot: int = 0
    poison_until: int = 0       # עד מתי הרעל פועל עליו
    poison_tick: int = 0        # מתי ירדו לו חיים מהרעל בפעם האחרונה


class Bullet(Entity):
    dx: float
    dy: float
    speed: float
    dmg: Range
    acc: float
    rng: float
    from_player: bool
    poison: bool = False        # חץ מורעל
    traveled: float = 0.0
    dead: bool = False


class Grenade(Entity):
    dx: float
    dy: float
    speed: float
    weapon: Weapon
    fuse: int           # מתי הרימון מתפוצץ
    rng: float
    radius: float
    traveled: float = 0.0
    dead: bool = False


class SmokeCloud(Entity):
    r: float
    until: int


class Spark(Entity):
    vx: float
    vy: float
    life: int
    color: Color


class Resource(Entity):
    kind: ResourceKind
    ready_at: int = 0


class Crate(Entity):
    kind: CrateKind
