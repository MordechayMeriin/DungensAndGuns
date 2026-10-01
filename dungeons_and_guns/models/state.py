# -*- coding: utf-8 -*-
"""מצב המשחק: השחקן, מה שיש לו, השלב הנוכחי, והודעות/קולות שמחכים להשמעה."""

from typing import Annotated, Any

from pydantic import (BaseModel, BeforeValidator, ConfigDict, Field, field_validator,
                      model_validator)

from ..config import TILE
from .catalog import WheelSlice
from .entities import Bullet, Crate, Enemy, Grenade, Resource, SmokeCloud, Spark
from .enums import ItemKind, MissionKind, ResourceKind, Tile

HOTBAR_SIZE = 10        # שורת המספרים: מקשים 1-9 ו-0
HOTBAR_KINDS = (ItemKind.WEAPON, ItemKind.POTION, ItemKind.FOOD)


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
    eat: bool = False


class Player(_Model):
    x: float
    y: float
    dir: tuple[float, float] = (0.0, 1.0)
    r: int = 11
    hp: float = 100
    max_hp: int = 100
    points: int = 0             # נקודות דרגה - מקבלים על כל אויב שמחסלים
    invuln: int = 0             # כמה פריימים השחקן עוד מוגן אחרי תחילת שלב
    sick: bool = False
    sick_tick: int = 0
    sick_nag: int = 0
    last_shot: int = 0
    last_interact: int = 0
    last_potion: int = 0
    last_meal: int = 0
    swing_until: int = 0
    swing_reach: float = 40

    @property
    def hp_ratio(self) -> float:
        return self.hp / self.max_hp


class SlotItem(_Model):
    """משהו שאפשר לשים בשורת המספרים: נשק (גם רימונים), תרופה או אוכל."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: ItemKind
    id: str

    @field_validator("kind")
    @classmethod
    def _usable(cls, kind: ItemKind) -> ItemKind:
        if kind not in HOTBAR_KINDS:
            raise ValueError("only weapons, potions and food go in the hotbar, not %s" % kind)
        return kind


class Inventory(_Model):
    money: int = 100
    weapons: list[str] = Field(default_factory=list)       # כל הנשקים שיש (גם רימונים)
    hotbar: list[SlotItem | None] = Field(default_factory=lambda: [None] * HOTBAR_SIZE)
    selected: int = Field(0, ge=0, lt=HOTBAR_SIZE)          # איזו משבצת בשורה נבחרה
    tools: set[str] = Field(default_factory=set)
    gear: set[str] = Field(default_factory=set)
    ammo: dict[str, int] = Field(default_factory=dict)       # סוג תחמושת -> כמה כדורים
    throwables: dict[str, int] = Field(default_factory=dict)  # רימון -> כמה יחידות
    potions: dict[str, int] = Field(default_factory=dict)
    keys: int = 0                                               # מפתחות לשערים
    oven_uses: int = 0                                          # כמה בישולים נשארו בתנור
    poison_arrows: int = 0                                      # כמה מהחיצים הבאים מורעלים
    food: dict[str, int] = Field(default_factory=dict)          # אוכל מהסדנה -> כמה מנות
    materials: dict[ResourceKind, int] = Field(default_factory=dict)  # משאב -> כמה פריטים נאספו

    @model_validator(mode="before")
    @classmethod
    def _fill_hotbar(cls, data: Any) -> Any:
        """משחק חדש, או שמירה מלפני שורת המספרים: מסדרים את השורה לבד."""
        if not isinstance(data, dict) or "hotbar" in data:
            return data
        data = dict(data)
        items = [SlotItem(kind=ItemKind.WEAPON, id=w) for w in data.get("weapons", [])]
        items += [SlotItem(kind=ItemKind.POTION, id=p) for p in data.get("potions", {})]
        items += [SlotItem(kind=ItemKind.FOOD, id=f) for f in data.get("food", {})]
        items = items[:HOTBAR_SIZE]
        data["hotbar"] = items + [None] * (HOTBAR_SIZE - len(items))
        data["selected"] = min(data.pop("weapon_index", 0), HOTBAR_SIZE - 1)
        return data

    @field_validator("hotbar")
    @classmethod
    def _hotbar_size(cls, hotbar: list[SlotItem | None]) -> list[SlotItem | None]:
        if len(hotbar) != HOTBAR_SIZE:
            raise ValueError("the hotbar has exactly %d slots" % HOTBAR_SIZE)
        return hotbar

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
        self.add_to_hotbar(SlotItem(kind=ItemKind.WEAPON, id=weapon_id))

    def potion_count(self, potion_id: str) -> int:
        return self.potions.get(potion_id, 0)

    def add_potion(self, potion_id: str, count: int = 1) -> None:
        self.potions[potion_id] = self.potions.get(potion_id, 0) + count
        self.add_to_hotbar(SlotItem(kind=ItemKind.POTION, id=potion_id))

    def food_count(self, food_id: str) -> int:
        return self.food.get(food_id, 0)

    def add_food(self, food_id: str, count: int = 1) -> None:
        self.food[food_id] = self.food.get(food_id, 0) + count
        self.add_to_hotbar(SlotItem(kind=ItemKind.FOOD, id=food_id))

    def material_count(self, kind: ResourceKind) -> int:
        return self.materials.get(kind, 0)

    def add_material(self, kind: ResourceKind, count: int = 1) -> None:
        self.materials[kind] = self.materials.get(kind, 0) + count

    # ---------- שורת המספרים ----------
    @property
    def selected_item(self) -> SlotItem | None:
        return self.hotbar[self.selected]

    def hotbar_index(self, item: SlotItem) -> int | None:
        return next((i for i, slot in enumerate(self.hotbar) if slot == item), None)

    def add_to_hotbar(self, item: SlotItem) -> None:
        """דבר חדש נכנס למשבצת הפנויה הראשונה (אם יש, ואם הוא עוד לא בשורה)."""
        if item in self.hotbar:
            return
        empty = next((i for i, slot in enumerate(self.hotbar) if slot is None), None)
        if empty is not None:
            self.hotbar[empty] = item

    def set_slot(self, index: int, item: SlotItem) -> None:
        """שם דבר במשבצת. אם הוא כבר במשבצת אחרת - שתי המשבצות מתחלפות."""
        old = self.hotbar_index(item)
        if old is not None:
            self.hotbar[old] = self.hotbar[index]
        self.hotbar[index] = item

    def clear_slot(self, index: int) -> None:
        self.hotbar[index] = None

    def select_slot(self, index: int) -> None:
        if 0 <= index < HOTBAR_SIZE:
            self.selected = index

    def cycle_slot(self, step: int) -> None:
        self.selected = (self.selected + step) % HOTBAR_SIZE


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
        """קיר, קיר משוריין או שער - עוצרים גם קליעים."""
        return self.tile_at(px, py).is_solid

    def blocked(self, px: float, py: float, boat: bool) -> bool:
        tile = self.tile_at(px, py)
        return tile.is_solid or (tile.is_water and not boat)

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


class Mission(_Model):
    """משימה עם שעון: לעשות משהו goal פעמים עד deadline (בזמן המשחק)."""

    kind: MissionKind
    goal: int = Field(gt=0)
    progress: int = 0
    deadline: int
    money: int              # הפרס
    points: int


class Weather(_Model):
    """ערפל שבא והולך (הזמנים לפי שעון המשחק)."""

    fog_start: int = 0
    fog_until: int = 0          # 0 = אין ערפל עכשיו
    next_fog_at: int = 0        # מתי יורד הערפל הבא (0 = עוד לא נקבע)


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
    mission: Mission | None = None
    weather: Weather = Field(default_factory=Weather)
    inspect_uid: int | None = None      # על איזה אויב לחצו כדי לראות את הנשק שלו
    inspect_until: int = 0

    def say(self, text: str) -> None:
        self.feedback.say(text)

    def play(self, name: str, gap: int = 0) -> None:
        self.feedback.play(name, gap)
