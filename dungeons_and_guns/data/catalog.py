# -*- coding: utf-8 -*-
"""הקטלוג: כל הפריטים של המשחק במקום אחד, עם בדיקה שהכל מתאים זה לזה."""

from functools import cached_property

from pydantic import BaseModel, ConfigDict, model_validator

from ..models import (AmmoType, Gear, GearCategory, Potion, ResourceKind, ResourceType, Tool,
                      Weapon, WeaponCategory, WeaponKind, WheelSlice, WheelTicket)


class Catalog(BaseModel):
    """Read-only registry of every item definition, with id lookups.

    Validation runs once at startup, so a typo in the data (an unknown ammo id, a duplicate
    weapon id, a resource that needs a tool that doesn't exist) fails loudly instead of
    crashing mid-game.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    weapons: list[Weapon]
    ammo_types: list[AmmoType]
    gear: list[Gear]
    tools: list[Tool]
    potions: list[Potion]
    resources: list[ResourceType]
    wheel_ticket: WheelTicket
    wheel_slices: list[WheelSlice]

    @model_validator(mode="after")
    def _check_references(self) -> "Catalog":
        for group in (self.weapons, self.ammo_types, self.gear, self.tools, self.potions):
            ids = [item.id for item in group]
            dupes = {i for i in ids if ids.count(i) > 1}
            if dupes:
                raise ValueError("duplicate ids: %s" % sorted(dupes))
        ammo_ids = {a.id for a in self.ammo_types}
        for w in self.weapons:
            if w.ammo is not None and w.ammo not in ammo_ids:
                raise ValueError("weapon %s uses unknown ammo %s" % (w.id, w.ammo))
        tool_ids = {t.id for t in self.tools}
        for r in self.resources:
            if r.tool is not None and r.tool not in tool_ids:
                raise ValueError("resource %s needs unknown tool %s" % (r.kind, r.tool))
        missing = set(ResourceKind) - {r.kind for r in self.resources}
        if missing:
            raise ValueError("resource kinds without a definition: %s" % sorted(missing))
        return self

    # ---------- חיפוש לפי id ----------
    @cached_property
    def _weapons(self) -> dict[str, Weapon]:
        return {w.id: w for w in self.weapons}

    @cached_property
    def _ammo(self) -> dict[str, AmmoType]:
        return {a.id: a for a in self.ammo_types}

    @cached_property
    def _tools(self) -> dict[str, Tool]:
        return {t.id: t for t in self.tools}

    @cached_property
    def _potions(self) -> dict[str, Potion]:
        return {p.id: p for p in self.potions}

    @cached_property
    def _resources(self) -> dict[ResourceKind, ResourceType]:
        return {r.kind: r for r in self.resources}

    def weapon(self, weapon_id: str) -> Weapon:
        return self._weapons[weapon_id]

    def ammo(self, ammo_id: str) -> AmmoType:
        return self._ammo[ammo_id]

    def ammo_for(self, weapon: Weapon) -> AmmoType | None:
        """איזו תחמושת הנשק צורך, או None אם הוא לא צורך בכלל."""
        return self._ammo[weapon.ammo] if weapon.ammo else None

    def tool(self, tool_id: str) -> Tool:
        return self._tools[tool_id]

    def potion(self, potion_id: str) -> Potion:
        return self._potions[potion_id]

    def resource(self, kind: ResourceKind) -> ResourceType:
        return self._resources[kind]

    # ---------- קבוצות ----------
    @property
    def weapon_categories(self) -> list[WeaponCategory]:
        return list(WeaponCategory)

    @property
    def gear_categories(self) -> list[GearCategory]:
        return list(GearCategory)

    @cached_property
    def throwables(self) -> list[Weapon]:
        return [w for w in self.weapons if w.kind == WeaponKind.THROW]

    @cached_property
    def enemy_weapons(self) -> list[Weapon]:
        """האויבים מקבלים רק נשק חם, מהזול ליקר, כך שבשלבים הראשונים הם חלשים."""
        return sorted((w for w in self.weapons
                       if w.kind == WeaponKind.GUN and w.cat != WeaponCategory.COLD),
                      key=lambda w: w.price)
