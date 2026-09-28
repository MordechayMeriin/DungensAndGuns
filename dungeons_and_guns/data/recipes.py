# -*- coding: utf-8 -*-
"""הסדנה: מה אפשר להכין מהחומרים שאוספים מהמשאבים (בולי עץ, מטילי ברזל...).

needs = איזה משאב וכמה פריטים ממנו. השמות של הפריטים עצמם כתובים ב-resources.py.
כלי נשק ותרופות לא מכינים בסדנה - רק קונים. אוכל להפך: רק מכינים.
"""

from ..models import ItemKind as I
from ..models import Recipe
from ..models import ResourceKind as R

RECIPES = [
    # תחמושת (חפיסה אחת לכל הכנה)
    Recipe(kind=I.AMMO, item="ammo_pistol",   needs={R.COPPER: 1, R.GAS: 1}),
    Recipe(kind=I.AMMO, item="ammo_revolver", needs={R.COPPER: 2, R.GAS: 1}),
    Recipe(kind=I.AMMO, item="ammo_smg",      needs={R.COPPER: 2, R.GAS: 1}),
    Recipe(kind=I.AMMO, item="ammo_rifle",    needs={R.COPPER: 2, R.GAS: 1, R.IRON: 1}),
    Recipe(kind=I.AMMO, item="ammo_ak",       needs={R.COPPER: 2, R.GAS: 1, R.IRON: 1}),
    Recipe(kind=I.AMMO, item="ammo_shell",    needs={R.COPPER: 1, R.GAS: 1, R.COTTON: 1}),
    Recipe(kind=I.AMMO, item="ammo_sniper",   needs={R.COPPER: 2, R.GAS: 1, R.GOLD: 1}),
    Recipe(kind=I.AMMO, item="ammo_mg",       needs={R.COPPER: 3, R.GAS: 2, R.IRON: 1}),
    Recipe(kind=I.AMMO, item="ammo_arrow",    needs={R.TREE: 2, R.IRON: 1}),
    # הגנה ושיפורי נשק
    Recipe(kind=I.GEAR, item="helmet",        needs={R.IRON: 2}),
    Recipe(kind=I.GEAR, item="shield",        needs={R.TREE: 2, R.IRON: 2}),
    Recipe(kind=I.GEAR, item="vest",          needs={R.IRON: 3, R.SHEEP: 2}),
    Recipe(kind=I.GEAR, item="sight",         needs={R.COPPER: 2, R.DIAMOND: 1}),
    Recipe(kind=I.GEAR, item="launcher",      needs={R.VOLCANO: 2, R.IRON: 2}),
    # מפתח לשערים
    Recipe(kind=I.KEY,  item="key",           needs={R.IRON: 1}),
    # אוכל מהחווה (אוכלים במקש F)
    Recipe(kind=I.FOOD, item="bread",         needs={R.WHEAT: 2}),
    Recipe(kind=I.FOOD, item="omelette",      needs={R.CHICKEN: 2}),
    Recipe(kind=I.FOOD, item="cheese",        needs={R.COW: 2}),
    Recipe(kind=I.FOOD, item="cake",          needs={R.WHEAT: 1, R.CHICKEN: 1, R.COW: 1}),
]
