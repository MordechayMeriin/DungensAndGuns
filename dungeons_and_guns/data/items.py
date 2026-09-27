# -*- coding: utf-8 -*-
"""תחמושת, ציוד, כלי עבודה, תרופות וגלגל המזל."""

from ..models import AmmoType, Gear, Potion, Tool, WheelSlice, WheelTicket
from ..models import GearCategory as G
from ..models import WheelOutcome as W

# סוגי תחמושת. נשק קר, רוגטקה ושוריקנים לא צורכים תחמושת בכלל.
AMMO_TYPES = [
    AmmoType(id="ammo_pistol",   name="כדורי אקדח",    pack=40, price=70,  desc="לאקדחים רגילים"),
    AmmoType(id="ammo_revolver", name="כדורי תופי",    pack=24, price=80,
             desc="לאקדחים התופיים (רוגר 101, סמית' אנד ווסון)"),
    AmmoType(id="ammo_smg",      name="כדורי תת מקלע", pack=60, price=100, desc="לעוזי, מק 10, MP5 ו-MP7"),
    AmmoType(id="ammo_rifle",    name="כדורי רובה",    pack=30, price=110, desc="לרובי סער מסוג M16, M4 ותבור"),
    AmmoType(id="ammo_ak",       name="כדורי AK",      pack=30, price=105, desc="לכל משפחת ה-AK ו-TYPE 56"),
    AmmoType(id="ammo_shell",    name="כדורי שוטגן",   pack=12, price=90,  desc="לרובי צייד"),
    AmmoType(id="ammo_sniper",   name="כדורי צלפים",   pack=10, price=150, desc="לרובי צלפים"),
    AmmoType(id="ammo_mg",       name="חגורת מקלע",    pack=60, price=200, desc="למקלעים כבדים"),
    AmmoType(id="ammo_arrow",    name="חיצים",         pack=15, price=60,  desc="לקשת", unit="חיצים"),
]

# ציוד שנקנה פעם אחת ועובד לבד (הגנה) או משפר את הנשק
GEAR = [
    Gear(id="shield", name="מגן", cat=G.PROTECTION, price=700, reduce=0.35, slow=0.18,
         desc="חוסם 35% מהנזק, אבל מאט את התנועה"),
    Gear(id="vest", name="שכפ\"ץ", cat=G.PROTECTION, price=900, reduce=0.30,
         desc="חוסם 30% מהנזק"),
    Gear(id="helmet", name="קסדה", cat=G.PROTECTION, price=400, reduce=0.15,
         desc="חוסמת 15% מהנזק"),
    Gear(id="sight", name="כוונת השלכה", cat=G.UPGRADES, price=500, acc=0.08, rng=0.08,
         desc="מוסיפה 8% דיוק וטווח לכל הנשקים"),
    Gear(id="laser", name="לייזר", cat=G.UPGRADES, price=400, acc=0.10,
         desc="מוסיף 10% דיוק ומראה קו כיוון"),
    Gear(id="launcher", name="מטול רימונים", cat=G.UPGRADES, price=1200,
         desc="הרימונים עפים רחוק יותר ומתפוצצים חזק יותר"),
]

TOOLS = [
    Tool(id="saw",     name="מסור", desc="נדרש לאיסוף עצים",          price=80),
    Tool(id="pickaxe", name="מכוש", desc="נדרש לכל המכרות ולהר הגעש", price=90),
    Tool(id="sickle",  name="מגל",  desc="נדרש לקציר חיטה וכותנה",    price=60),
    Tool(id="rod",     name="חכה",  desc="נדרש לדוג במים עם דגים",    price=70),
    Tool(id="torch",   name="לפיד", desc="נדרש כדי להיכנס למערות",    price=50),
    Tool(id="boat",    name="סירה", desc="מאפשרת לעבור מעל המים",     price=150),
]

POTIONS = [
    Potion(id="small",  name="תרופה קטנה",    heal=25,  price=40,  art="potion_small"),
    Potion(id="medium", name="תרופה בינונית", heal=60,  price=90,  art="potion_medium"),
    Potion(id="large",  name="תרופה גדולה",   heal=120, price=160, art="potion_large"),
]

# גלגל המזל - שבע משבצות טובות ושלוש רעות, מפוזרות מסביב
WHEEL_TICKET = WheelTicket(id="wheel", name="גלגל המזל", price=200,
                           desc="סיבוב אחד: אפשר לזכות בנשק, כסף או ציוד - ואפשר גם להפסיד")
WHEEL_SLICES = [
    WheelSlice(id=W.MONEY,      name="כסף",        color=(226, 186, 54),  good=True),
    WheelSlice(id=W.SICK,       name="מחלה",       color=(118, 156, 96),  good=False),
    WheelSlice(id=W.POTION,     name="תרופה",      color=(216, 62, 74),   good=True),
    WheelSlice(id=W.LOSE_MONEY, name="מינוס כסף",  color=(176, 92, 40),   good=False),
    WheelSlice(id=W.GRENADES,   name="רימונים",    color=(104, 128, 78),  good=True),
    WheelSlice(id=W.WEAPON,     name="נשק",        color=(126, 130, 142), good=True),
    WheelSlice(id=W.LOSE_HP,    name="מינוס חיים", color=(198, 52, 52),   good=False),
    WheelSlice(id=W.TOOL,       name="כלי עבודה",  color=(150, 100, 52),  good=True),
    WheelSlice(id=W.GEAR,       name="ציוד",       color=(92, 120, 164),  good=True),
    WheelSlice(id=W.HEAL,       name="חיים מלאים", color=(62, 190, 90),   good=True),
]
