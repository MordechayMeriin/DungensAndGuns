# -*- coding: utf-8 -*-
"""הקטלוג: כל הפריטים של המשחק במקום אחד, עם בדיקה שהכל מתאים זה לזה."""

from functools import cached_property

from pydantic import BaseModel, ConfigDict, model_validator

from ..models import (AmmoType, Food, Gear, GearCategory, ItemBase, ItemKind, Key, Material, Oven, Poison, Potion, Quiver, Rank, Recipe, ResourceKind,
                      ResourceType, Tool, Weapon, WeaponCategory, WeaponKind, WheelSlice,
                      WheelTicket)


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
    foods: list[Food]
    key: Key
    oven: Oven
    poison: Poison
    quiver: Quiver
    resources: list[ResourceType]
    materials: list[Material]
    recipes: list[Recipe]
    ranks: list[Rank]
    wheel_ticket: WheelTicket
    wheel_slices: list[WheelSlice]

    @model_validator(mode="after")
    def _check_references(self) -> "Catalog":
        for group in (self.weapons, self.ammo_types, self.gear, self.tools, self.potions,
                      self.foods):
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
        materials = {m.id for m in self.materials}
        foods = {f.id for f in self.foods}
        for r in self.resources:
            if not set(r.drops) <= materials or (r.food is not None and r.food not in foods):
                raise ValueError("resource %s drops unknown things" % r.kind)
        for recipe in self.recipes:
            try:
                item = self.item(recipe.kind, recipe.item)
            except KeyError:
                raise ValueError("recipe makes unknown %s %s" % (recipe.kind, recipe.item)) from None
            if (recipe.kind == ItemKind.THROWABLE) != (isinstance(item, Weapon) and item.is_throwable):
                raise ValueError("recipe %s: throwables and only throwables use kind THROWABLE"
                                 % recipe.item)
            unknown = set(recipe.potions) - {p.id for p in self.potions}
            if unknown:
                raise ValueError("recipe %s needs unknown potions: %s" % (recipe.item, sorted(unknown)))
            if not set(recipe.needs) <= materials:
                raise ValueError("recipe %s needs unknown materials: %s"
                                 % (recipe.item, sorted(set(recipe.needs) - materials)))
        if self.quiver.ammo not in ammo_ids:
            raise ValueError("quiver is for unknown ammo %s" % self.quiver.ammo)
        if self.poison.ammo not in ammo_ids:
            raise ValueError("poison is for unknown ammo %s" % self.poison.ammo)
        food_ids = {f.id for f in self.foods}
        for f in self.foods:
            if f.cooks_into is not None and (f.cooks_into not in food_ids
                                             or self.food(f.cooks_into).raw):
                raise ValueError("food %s cooks into %s, which is not a cooked food"
                                 % (f.id, f.cooks_into))
        points = [r.points for r in self.ranks]
        if not points or points[0] != 0 or points != sorted(set(points)):
            raise ValueError("ranks must start at 0 points and go strictly up: %s" % points)
        weapon_ids = {w.id for w in self.weapons}
        unlocks = [wid for r in self.ranks for wid in r.unlocks]
        if len(unlocks) != len(set(unlocks)):
            raise ValueError("a weapon is unlocked by more than one rank")
        if not set(unlocks) <= weapon_ids:
            raise ValueError("ranks unlock unknown weapons: %s" % sorted(set(unlocks) - weapon_ids))
        return self

    # ---------- חיפוש לפי id ----------
    @cached_property
    def _weapons(self) -> dict[str, Weapon]:
        return {w.id: w for w in self.weapons}

    @cached_property
    def _ammo(self) -> dict[str, AmmoType]:
        return {a.id: a for a in self.ammo_types}

    @cached_property
    def _gear(self) -> dict[str, Gear]:
        return {g.id: g for g in self.gear}

    @cached_property
    def _tools(self) -> dict[str, Tool]:
        return {t.id: t for t in self.tools}

    @cached_property
    def _potions(self) -> dict[str, Potion]:
        return {p.id: p for p in self.potions}

    @cached_property
    def _foods(self) -> dict[str, Food]:
        return {f.id: f for f in self.foods}

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

    def food(self, food_id: str) -> Food:
        return self._foods[food_id]

    def resource(self, kind: ResourceKind) -> ResourceType:
        return self._resources[kind]

    def material(self, material_id: str) -> Material:
        return self._materials[material_id]

    @cached_property
    def _materials(self) -> dict[str, Material]:
        return {m.id: m for m in self.materials}

    def item(self, kind: ItemKind, item_id: str) -> ItemBase:
        """פריט לפי הסוג שלו וה-id (זורק KeyError אם אין כזה)."""
        match kind:
            case ItemKind.WEAPON | ItemKind.THROWABLE:
                return self.weapon(item_id)
            case ItemKind.AMMO:
                return self.ammo(item_id)
            case ItemKind.TOOL:
                return self.tool(item_id)
            case ItemKind.POTION:
                return self.potion(item_id)
            case ItemKind.GEAR:
                return self._gear[item_id]
            case ItemKind.FOOD:
                return self.food(item_id)
            case ItemKind.KEY | ItemKind.OVEN | ItemKind.POISON | ItemKind.QUIVER:
                single = {ItemKind.KEY: self.key, ItemKind.OVEN: self.oven,
                          ItemKind.POISON: self.poison, ItemKind.QUIVER: self.quiver}[kind]
                if item_id != single.id:
                    raise KeyError(item_id)
                return single

    def rank_for(self, points: int) -> Rank:
        """הדרגה הכי גבוהה שהנקודות מספיקות לה."""
        return [r for r in self.ranks if r.points <= points][-1]

    def next_rank(self, points: int) -> Rank | None:
        return next((r for r in self.ranks if r.points > points), None)

    def unlock_rank(self, weapon_id: str) -> Rank | None:
        """איזו דרגה פותחת את הנשק (None = פתוח מההתחלה)."""
        return next((r for r in self.ranks if weapon_id in r.unlocks), None)

    # ---------- קבוצות ----------
    @property
    def weapon_categories(self) -> list[WeaponCategory]:
        return list(WeaponCategory)

    @property
    def gear_categories(self) -> list[GearCategory]:
        return list(GearCategory)

    @cached_property
    def food_types(self) -> list[Food]:
        """סוגי האוכל (המבושלים - 6 היום). אוכל נא נחשב כמו מה שהוא נהיה כשמבשלים: בצק = לחם."""
        return [f for f in self.foods if not f.raw]

    def food_type(self, food: Food) -> str:
        return food.cooks_into or food.id

    @cached_property
    def raw_foods(self) -> list[Food]:
        return [f for f in self.foods if f.raw]

    @cached_property
    def throwables(self) -> list[Weapon]:
        return [w for w in self.weapons if w.kind == WeaponKind.THROW]

    @cached_property
    def enemy_weapons(self) -> list[Weapon]:
        """הנשקים של האויבים (חם וקר, בלי רימונים), מהזול ליקר - בשלבים הראשונים הם חלשים."""
        return sorted((w for w in self.weapons if w.kind in (WeaponKind.GUN, WeaponKind.MELEE)),
                      key=lambda w: w.price)
