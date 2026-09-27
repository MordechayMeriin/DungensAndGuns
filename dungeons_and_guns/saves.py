# -*- coding: utf-8 -*-
"""שמירה וטעינה של משחקים לקבצים בתיקייה saves.

Each slot is one JSON file holding a ``SaveGame`` (the whole ``GameState`` plus metadata).
pydantic does the (de)serialization and validation, so a damaged or incompatible file is
reported as such instead of crashing the game.
"""

import os
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .config import SAVE_DIR
from .models import GameState

SAVE_VERSION = 1            # להעלות כשמבנה GameState משתנה בצורה ששוברת קבצים ישנים
SLOT_COUNT = 3


class SaveError(Exception):
    """הקובץ חסר, פגום, או שנשמר בגרסה אחרת של המשחק."""


class SaveGame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = SAVE_VERSION
    saved_at: datetime = Field(default_factory=datetime.now)
    state: GameState


class SlotInfo(BaseModel):
    """מה מראים על משבצת שמירה בתפריט, בלי לטעון את כל המשחק לתוכו."""

    model_config = ConfigDict(frozen=True)

    slot: int
    exists: bool = False
    damaged: bool = False
    level: int = 0
    money: int = 0
    hp: int = 0
    saved_at: datetime | None = None

    @property
    def loadable(self) -> bool:
        return self.exists and not self.damaged


class SaveStore:
    def __init__(self, directory: str = SAVE_DIR, slot_count: int = SLOT_COUNT):
        self.directory = directory
        self.slot_count = slot_count

    def path(self, slot: int) -> str:
        return os.path.join(self.directory, "slot%d.json" % slot)

    def save(self, slot: int, state: GameState) -> None:
        os.makedirs(self.directory, exist_ok=True)
        data = SaveGame(state=state).model_dump_json(indent=1)
        # כותבים לקובץ זמני ואז מחליפים - כך קריסה באמצע לא הורסת שמירה קודמת
        tmp = self.path(slot) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, self.path(slot))

    def _read(self, slot: int) -> SaveGame:
        try:
            with open(self.path(slot), encoding="utf-8") as f:
                save = SaveGame.model_validate_json(f.read())
        except FileNotFoundError as e:
            raise SaveError("empty slot") from e
        except (OSError, ValueError, ValidationError) as e:
            raise SaveError("damaged save: %s" % e) from e
        if save.version != SAVE_VERSION:
            raise SaveError("save version %d, game expects %d" % (save.version, SAVE_VERSION))
        return save

    def load(self, slot: int) -> GameState:
        state = self._read(slot).state
        state.feedback.sounds.clear()
        return state

    def slot_info(self, slot: int) -> SlotInfo:
        if not os.path.exists(self.path(slot)):
            return SlotInfo(slot=slot)
        try:
            save = self._read(slot)
        except SaveError:
            return SlotInfo(slot=slot, exists=True, damaged=True)
        state = save.state
        return SlotInfo(slot=slot, exists=True, level=state.level.number,
                        money=state.inventory.money, hp=round(state.player.hp),
                        saved_at=save.saved_at)

    def slots(self) -> list[SlotInfo]:
        return [self.slot_info(i) for i in range(1, self.slot_count + 1)]

    def any_loadable(self) -> bool:
        return any(s.loadable for s in self.slots())
