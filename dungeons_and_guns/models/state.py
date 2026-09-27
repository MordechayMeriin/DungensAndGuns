# -*- coding: utf-8 -*-
"""מצב המשחק: השחקן, מה שיש לו, השלב הנוכחי, והודעות/קולות שמחכים להשמעה."""

from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from ..config import TILE
from .catalog import WheelSlice
from .entities import Bullet, Crate, Enemy, Grenade, Resource, SmokeCloud, Spark
from .enums import Tile



def _parse_point(value: Any) -> Any:
    """JSON keys are strings: a saved (3, 5) comes back as "3,5"."""
    if isinstance(value, str):
        x, y = value.split(",")
        return int(x), int(y)
    return value


Point = tuple[int, int]
PointKey = Annotated[Point, BeforeValidator(_parse_point)]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PlayerInput(_Model):
    """מה השחקן מבקש לעשות בפריים הזה (ה-app מתרגם מקשים לזה)."""

    dx: float = 0.0
    dy: float = 0.0
    shoot: bool = False
    interact: bool = False
    drink: bool = False


class Player(_Model):
    x: float
    y: float
    dir: tuple[float, float] = (0.0, 1.0)
    r: int = 11
    hp: float = 100
    max_hp: int = 100
    invuln: int = 0             # כמה פריימים השחקן עוד מוגן אחרי תחילת שלב
    sick: bool = False
    sick_tick: int = 0
    sick_nag: int = 0
    last_shot: int = 0
    last_interact: int = 0
    last_potion: int = 0
    swing_until: int = 0
    swing_reach: float = 40

    @property
    def hp_ratio(self) -> float:
        return self.hp / self.max_hp


class Inventory(_Model):
    money: int = 100
    weapons: list[str] = Field(default_factory=list)       # לפי הסדר של מקשי 1-9
    weapon_index: int = 0
    tools: set[str] = Field(default_factory=set)
    gear: set[str] = Field(default_factory=set)
    ammo: dict[str, int] = Field(default_factory=dict)       # סוג תחמושת -> כמה כדורים
    throwables: dict[str, int] = Field(default_factory=dict)  # רימון -> כמה יחידות
    potions: dict[str, int] = Field(default_factory=dict)

    @property
    def weapon_id(self) -> str:
        return self.weapons[self.weapon_index]

    def ammo_count(self, ammo_id: str) -> int:
        return self.ammo.get(ammo_id, 0)

    def add_ammo(self, ammo_id: str, count: int) -> None:
        self.ammo[ammo_id] = self.ammo.get(ammo_id, 0) + count

    def throwable_count(self, weapon_id: str) -> int:
        return self.throwables.get(weapon_id, 0)

    def add_throwable(self, weapon_id: str, count: int) -> None:
        self.throwables[weapon_id] = self.throwables.get(weapon_id, 0) + count
        if weapon_id not in self.weapons:
            self.weapons.append(weapon_id)

    def potion_count(self, potion_id: str) -> int:
        return self.potions.get(potion_id, 0)

    def add_potion(self, potion_id: str, count: int = 1) -> None:
        self.potions[potion_id] = self.potions.get(potion_id, 0) + count

    def cycle_weapon(self, step: int) -> None:
        if self.weapons:
            self.weapon_index = (self.weapon_index + step) % len(self.weapons)

    def select_weapon(self, index: int) -> None:
        if 0 <= index < len(self.weapons):
            self.weapon_index = index


class Level(_Model):
    """מבוך אחד וכל מה שבתוכו."""

    number: int
    cols: int
    rows: int
    grid: list[list[Tile]]
    exit_tile: Point
    max_weapon: int                     # עד איזה נשק (ברשימה הממוינת) האויבים מקבלים
    enemies: list[Enemy] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)
    crates: list[Crate] = Field(default_factory=list)
    fish_cooldown: dict[PointKey, int] = Field(default_factory=dict)
    bullets: list[Bullet] = Field(default_factory=list)
    grenades: list[Grenade] = Field(default_factory=list)
    smokes: list[SmokeCloud] = Field(default_factory=list)
    sparks: list[Spark] = Field(default_factory=list)

    @property
    def width(self) -> int:
        return self.cols * TILE

    @property
    def height(self) -> int:
        return self.rows * TILE

    def tile_at(self, px: float, py: float) -> Tile:
        gx, gy = int(px // TILE), int(py // TILE)
        if gx < 0 or gy < 0 or gx >= self.cols or gy >= self.rows:
            return Tile.WALL
        return self.grid[gy][gx]

    def is_wall(self, px: float, py: float) -> bool:
        return self.tile_at(px, py) == Tile.WALL

    def blocked(self, px: float, py: float, boat: bool) -> bool:
        tile = self.tile_at(px, py)
        return tile == Tile.WALL or (tile.is_water and not boat)

    def can_move(self, x: float, y: float, r: float, boat: bool = False) -> bool:
        return not (self.blocked(x - r, y - r, boat) or self.blocked(x + r, y - r, boat) or
                    self.blocked(x - r, y + r, boat) or self.blocked(x + r, y + r, boat))

    def enemy_by_uid(self, uid: int | None) -> Enemy | None:
        return next((e for e in self.enemies if e.uid == uid), None)


class SoundCue(_Model):
    name: str
    gap: int = 0        # כמה מילישניות לחכות לפני שאותו קול חוזר


class Feedback(_Model):
    """הודעה על המסך וקולות שמחכים שה-app ינגן אותם."""

    message: str = ""
    message_timer: int = 0
    sounds: list[SoundCue] = Field(default_factory=list, exclude=True)   # לא נשמר לקובץ

    def say(self, text: str) -> None:
        self.message = text
        self.message_timer = 120

    def play(self, name: str, gap: int = 0) -> None:
        self.sounds.append(SoundCue(name=name, gap=gap))

    def tick(self) -> None:
        """נקרא פעם בפריים - ההודעה נעלמת אחרי כמה שניות."""
        if self.message_timer > 0:
            self.message_timer -= 1

    def drain_sounds(self) -> list[SoundCue]:
        cues, self.sounds = self.sounds, []
        return cues


class WheelSpin(_Model):
    angle: float
    speed: float
    done: bool = False
    result: WheelSlice | None = None
    last_index: int = -1
    text: str = ""


class GameState(_Model):
    # שעון המשחק במילישניות. ה-app מקדם אותו בכל פריים (לא בזמן התפריט), וכל הזמנים
    # האחרים (טעינת נשק, פתיל רימון, צמיחת חיטה...) נמדדים לפיו - כך הם נשמרים נכון לקובץ.
    now: int = 0
    player: Player
    inventory: Inventory
    level: Level
    feedback: Feedback = Field(default_factory=Feedback)
    game_over: bool = False
    wheel: WheelSpin | None = None
    inspect_uid: int | None = None      # על איזה אויב לחצו כדי לראות את הנשק שלו
    inspect_until: int = 0

    def say(self, text: str) -> None:
        self.feedback.say(text)

    def play(self, name: str, gap: int = 0) -> None:
        self.feedback.play(name, gap)
