# -*- coding: utf-8 -*-
"""הסדנה: מה אפשר להכין מהחומרים שאוספים מהמשאבים (בולי עץ, מטילי ברזל...).

needs = איזה חומר וכמה ממנו (החומרים כתובים ב-materials.py).
כלי נשק, ציוד (הגנה ושיפורי נשק) ותרופות לא מכינים בסדנה - רק קונים. אוכל ותנור להפך: רק מכינים.
האוכל יוצא נא - מבשלים אותו בתנור (גם זה בסדנה).
"""

from ..models import ItemKind as I
from ..models import Recipe

RECIPES = [
    # תחמושת (חפיסה אחת לכל הכנה)
    Recipe(kind=I.AMMO, item="ammo_pistol",   needs={"copper": 1, "gas": 1}),
    Recipe(kind=I.AMMO, item="ammo_mini",     needs={"copper": 1}),
    Recipe(kind=I.AMMO, item="ammo_revolver", needs={"copper": 2, "gas": 1}),
    Recipe(kind=I.AMMO, item="ammo_smg",      needs={"copper": 2, "gas": 1}),
    Recipe(kind=I.AMMO, item="ammo_rifle",    needs={"copper": 2, "gas": 1, "iron": 1}),
    Recipe(kind=I.AMMO, item="ammo_ak",       needs={"copper": 2, "gas": 1, "iron": 1}),
    Recipe(kind=I.AMMO, item="ammo_shell",    needs={"copper": 1, "gas": 1, "cotton": 1}),
    Recipe(kind=I.AMMO, item="ammo_sniper",   needs={"copper": 2, "gas": 1, "gold": 1}),
    Recipe(kind=I.AMMO, item="ammo_mg",       needs={"copper": 3, "gas": 2, "iron": 1}),
    Recipe(kind=I.AMMO, item="ammo_arrow",    needs={"log": 2, "iron": 1}),
    # אשפת חיצים מעור (פעם אחת)
    Recipe(kind=I.QUIVER, item="quiver",      needs={"leather": 1}),
    # מפתח לשערים - מעצם
    Recipe(kind=I.KEY,  item="key",           needs={"bone": 1}),
    # רעל לחיצים: תרופה בינונית + כותנה + צמר
    Recipe(kind=I.POISON, item="poison",      needs={"cotton": 1, "wool": 1}, potions={"medium": 1}),
    # תנור מלבנה אחת (3 בישולים)
    Recipe(kind=I.OVEN, item="oven",          needs={"brick": 1}),
    # אוכל מהחווה (אוכלים במקש F) - יוצא נא, מבשלים בתנור
    Recipe(kind=I.FOOD, item="dough",         needs={"wheat": 2}),
    Recipe(kind=I.FOOD, item="eggs",          needs={"egg": 2}),
    Recipe(kind=I.FOOD, item="cheese",        needs={"milk": 2}),
    Recipe(kind=I.FOOD, item="batter",        needs={"wheat": 1, "egg": 1, "milk": 1}),
]
