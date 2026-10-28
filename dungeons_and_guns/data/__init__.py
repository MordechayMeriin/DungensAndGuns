# -*- coding: utf-8 -*-
"""התוכן של המשחק. להוספת נשק/כלי/משאב/מתכון/דרגה חדשים - עורכים את הקבצים בתיקייה הזו."""

from .catalog import Catalog
from .materials import MATERIALS
from .items import AMMO_TYPES, FOODS, GEAR, KEY, OVEN, POISON, POTIONS, QUIVER, TOOLS, WHEEL_SLICES, WHEEL_TICKET
from .ranks import RANKS
from .recipes import RECIPES
from .resources import RESOURCE_TYPES
from .weapons import WEAPONS

CATALOG = Catalog(
    weapons=WEAPONS,
    ammo_types=AMMO_TYPES,
    gear=GEAR,
    tools=TOOLS,
    potions=POTIONS,
    foods=FOODS,
    key=KEY,
    oven=OVEN,
    poison=POISON,
    quiver=QUIVER,
    resources=RESOURCE_TYPES,
    materials=MATERIALS,
    recipes=RECIPES,
    ranks=RANKS,
    wheel_ticket=WHEEL_TICKET,
    wheel_slices=WHEEL_SLICES,
)

__all__ = ["CATALOG", "Catalog"]
