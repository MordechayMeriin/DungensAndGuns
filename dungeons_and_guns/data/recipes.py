# -*- coding: utf-8 -*-
"""הסדנה: מה אפשר להכין מהחומרים שאוספים מהמשאבים (בולי עץ, מטילי ברזל...).

needs = איזה משאב וכמה פריטים ממנו. השמות של הפריטים עצמם כתובים ב-resources.py.
כלי נשק, ציוד (הגנה ושיפורי נשק) ותרופות לא מכינים בסדנה - רק קונים. אוכל ותנור להפך: רק מכינים.
האוכל יוצא נא - מבשלים אותו בתנור (גם זה בסדנה).
"""

from ..models import ItemKind as I
from ..models import Recipe
from ..models import ResourceKind as R

RECIPES = [
    # תחמושת (חפיסה אחת לכל הכנה)
    Recipe(kind=I.AMMO, item="ammo_pistol",   needs={R.COPPER: 1, R.GAS: 1}),
    Recipe(kind=I.AMMO, item="ammo_mini",     needs={R.COPPER: 1}),
    Recipe(kind=I.AMMO, item="ammo_revolver", needs={R.COPPER: 2, R.GAS: 1}),
    Recipe(kind=I.AMMO, item="ammo_smg",      needs={R.COPPER: 2, R.GAS: 1}),
    Recipe(kind=I.AMMO, item="ammo_rifle",    needs={R.COPPER: 2, R.GAS: 1, R.IRON: 1}),
    Recipe(kind=I.AMMO, item="ammo_ak",       needs={R.COPPER: 2, R.GAS: 1, R.IRON: 1}),
    Recipe(kind=I.AMMO, item="ammo_shell",    needs={R.COPPER: 1, R.GAS: 1, R.COTTON: 1}),
    Recipe(kind=I.AMMO, item="ammo_sniper",   needs={R.COPPER: 2, R.GAS: 1, R.GOLD: 1}),
    Recipe(kind=I.AMMO, item="ammo_mg",       needs={R.COPPER: 3, R.GAS: 2, R.IRON: 1}),
    Recipe(kind=I.AMMO, item="ammo_arrow",    needs={R.TREE: 2, R.IRON: 1}),
    # מפתח לשערים
    Recipe(kind=I.KEY,  item="key",           needs={R.IRON: 1}),
    # רעל לחיצים: תרופה בינונית + כותנה + צמר
    Recipe(kind=I.POISON, item="poison",      needs={R.COTTON: 1, R.SHEEP: 1}, potions={"medium": 1}),
    # תנור מלבנה אחת (3 בישולים)
    Recipe(kind=I.OVEN, item="oven",          needs={R.BRICKS: 1}),
    # אוכל מהחווה (אוכלים במקש F) - יוצא נא, מבשלים בתנור
    Recipe(kind=I.FOOD, item="dough",         needs={R.WHEAT: 2}),
    Recipe(kind=I.FOOD, item="eggs",          needs={R.CHICKEN: 2}),
    Recipe(kind=I.FOOD, item="cheese",        needs={R.COW: 2}),
    Recipe(kind=I.FOOD, item="batter",        needs={R.WHEAT: 1, R.CHICKEN: 1, R.COW: 1}),
]
