# -*- coding: utf-8 -*-
"""התוכן של המשחק. להוספת נשק/כלי/משאב חדש - עורכים את הקבצים בתיקייה הזו."""

from .catalog import Catalog
from .items import AMMO_TYPES, GEAR, POTIONS, TOOLS, WHEEL_SLICES, WHEEL_TICKET
from .resources import RESOURCE_TYPES
from .weapons import WEAPONS

CATALOG = Catalog(
    weapons=WEAPONS,
    ammo_types=AMMO_TYPES,
    gear=GEAR,
    tools=TOOLS,
    potions=POTIONS,
    resources=RESOURCE_TYPES,
    wheel_ticket=WHEEL_TICKET,
    wheel_slices=WHEEL_SLICES,
)

__all__ = ["CATALOG", "Catalog"]
