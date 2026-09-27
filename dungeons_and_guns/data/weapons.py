# -*- coding: utf-8 -*-
"""כל כלי הנשק במשחק.

kind: GUN = יורה קליעים | MELEE = מכה מקרוב | THROW = זריקת רימון
art  = איזה ציור להשתמש בו כשאין תצלום אמיתי לפריט
ammo = נקבע לבד לפי המחלקה; כותבים אותו רק לנשק שצורך תחמושת אחרת
"""

from ..models import Weapon
from ..models import WeaponCategory as C
from ..models import WeaponKind as K

WEAPONS = [
    # ----- אקדחים -----
    Weapon(id="ruger101",  name="רוגר 101 תופי",   cat=C.PISTOLS, art="revolver", kind=K.GUN, dmg=(18, 26), acc=0.78, rng=210, cooldown=520, price=180, ammo="ammo_revolver"),
    Weapon(id="beretta",   name="ברטה מיני",       cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(6, 10),  acc=0.70, rng=150, cooldown=220, price=90),
    Weapon(id="cz75",      name="CZ 75 קומפקט",    cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(10, 15), acc=0.78, rng=230, cooldown=250, price=170),
    Weapon(id="czp",       name="CZ P-10",         cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(11, 16), acc=0.79, rng=235, cooldown=240, price=200),
    Weapon(id="glock26",   name="גלוק 26",         cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(8, 13),  acc=0.74, rng=200, cooldown=250, price=130),
    Weapon(id="glock19",   name="גלוק 19",         cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(9, 14),  acc=0.80, rng=220, cooldown=260, price=0),
    Weapon(id="glock17",   name="גלוק 17",         cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(10, 15), acc=0.81, rng=240, cooldown=250, price=180),
    Weapon(id="glock47",   name="גלוק 47",         cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(11, 16), acc=0.82, rng=250, cooldown=245, price=220),
    Weapon(id="sig",       name="זיג זאואר",       cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(11, 17), acc=0.80, rng=245, cooldown=255, price=240),
    Weapon(id="smith",     name="סמית' אנד ווסון", cat=C.PISTOLS, art="revolver", kind=K.GUN, dmg=(16, 24), acc=0.76, rng=215, cooldown=480, price=260, ammo="ammo_revolver"),
    Weapon(id="masada",    name="מצדה",            cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(12, 17), acc=0.82, rng=250, cooldown=235, price=290),
    Weapon(id="jericho",   name="יריחו",           cat=C.PISTOLS, art="pistol",   kind=K.GUN, dmg=(12, 18), acc=0.80, rng=245, cooldown=240, price=270),

    # ----- רובי צייד -----
    Weapon(id="shotgun",   name="שוטגן",           cat=C.SHOTGUNS, art="shotgun", kind=K.GUN, dmg=(7, 12), acc=0.55, rng=150, cooldown=780, price=600, pellets=6),

    # ----- תתי מקלע -----
    Weapon(id="uzi",       name="עוזי",            cat=C.SMGS, art="smg", kind=K.GUN, dmg=(5, 9),  acc=0.58, rng=170, cooldown=90,  price=450),
    Weapon(id="mac10",     name="מק 10",           cat=C.SMGS, art="smg", kind=K.GUN, dmg=(5, 9),  acc=0.50, rng=150, cooldown=70,  price=480),
    Weapon(id="mp5",       name="MP5",             cat=C.SMGS, art="smg", kind=K.GUN, dmg=(6, 11), acc=0.64, rng=200, cooldown=100, price=620),
    Weapon(id="mp7",       name="MP7",             cat=C.SMGS, art="smg", kind=K.GUN, dmg=(7, 11), acc=0.66, rng=210, cooldown=85,  price=750),

    # ----- רובי סער -----
    Weapon(id="m16",       name="M16",             cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(13, 19), acc=0.66, rng=330, cooldown=170, price=900),
    Weapon(id="m16a1",     name="M16A1",           cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(14, 19), acc=0.67, rng=335, cooldown=165, price=950),
    Weapon(id="m16a2",     name="M16A2",           cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(14, 20), acc=0.69, rng=345, cooldown=160, price=1000),
    Weapon(id="m16a3",     name="M16A3",           cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(15, 20), acc=0.70, rng=350, cooldown=150, price=1050),
    Weapon(id="m16a4",     name="M16A4",           cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(15, 21), acc=0.72, rng=355, cooldown=145, price=1100),
    Weapon(id="m4",        name="M4",              cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(13, 18), acc=0.68, rng=300, cooldown=140, price=1000),
    Weapon(id="m4a1",      name="M4A1",            cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(14, 19), acc=0.70, rng=305, cooldown=130, price=1100),
    Weapon(id="m4a2",      name="M4A2",            cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(14, 19), acc=0.71, rng=310, cooldown=128, price=1150),
    Weapon(id="m4a3",      name="M4A3",            cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(15, 20), acc=0.72, rng=315, cooldown=125, price=1200),
    Weapon(id="m4a4",      name="M4A4",            cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(15, 21), acc=0.73, rng=320, cooldown=120, price=1250),
    Weapon(id="ak47",      name="AK-47",           cat=C.RIFLES, art="ar_ak",  kind=K.GUN, dmg=(16, 22), acc=0.62, rng=320, cooldown=190, price=950, ammo="ammo_ak"),
    Weapon(id="aks47",     name="AKS-47",          cat=C.RIFLES, art="ar_ak",  kind=K.GUN, dmg=(16, 22), acc=0.61, rng=315, cooldown=185, price=980, ammo="ammo_ak"),
    Weapon(id="akm",       name="AKM",             cat=C.RIFLES, art="ar_ak",  kind=K.GUN, dmg=(16, 23), acc=0.64, rng=325, cooldown=180, price=1050, ammo="ammo_ak"),
    Weapon(id="akms",      name="AKMS",            cat=C.RIFLES, art="ar_ak",  kind=K.GUN, dmg=(16, 23), acc=0.63, rng=320, cooldown=175, price=1080, ammo="ammo_ak"),
    Weapon(id="type56",    name="TYPE 56",         cat=C.RIFLES, art="ar_ak",  kind=K.GUN, dmg=(15, 22), acc=0.60, rng=310, cooldown=185, price=900, ammo="ammo_ak"),
    Weapon(id="tavor",     name="תבור X95",        cat=C.RIFLES, art="ar_m16", kind=K.GUN, dmg=(16, 22), acc=0.74, rng=330, cooldown=140, price=1400),

    # ----- רובי צלפים -----
    Weapon(id="barak",     name="ברק",             cat=C.SNIPERS, art="sniper",     kind=K.GUN, dmg=(45, 60),  acc=0.88, rng=520, cooldown=900,  price=1500, speed=13),
    Weapon(id="barrett82", name="בארט M82A1",      cat=C.SNIPERS, art="sniper_big", kind=K.GUN, dmg=(80, 105), acc=0.88, rng=700, cooldown=1250, price=2600, speed=15),
    Weapon(id="remington", name="רמינגטון",        cat=C.SNIPERS, art="sniper",     kind=K.GUN, dmg=(50, 70),  acc=0.90, rng=560, cooldown=950,  price=1800, speed=13),
    Weapon(id="tango51",   name="טנגו 51",         cat=C.SNIPERS, art="sniper",     kind=K.GUN, dmg=(60, 80),  acc=0.93, rng=620, cooldown=1000, price=2100, speed=14),
    Weapon(id="blaser",    name="בלייזר",          cat=C.SNIPERS, art="sniper",     kind=K.GUN, dmg=(65, 85),  acc=0.92, rng=650, cooldown=1050, price=2300, speed=14),
    Weapon(id="dragunov",  name="דרגונוב",         cat=C.SNIPERS, art="sniper",     kind=K.GUN, dmg=(40, 55),  acc=0.85, rng=540, cooldown=650,  price=1700, speed=13),

    # ----- מקלעים כבדים -----
    Weapon(id="mag",       name="מאג",             cat=C.HEAVY, art="mg",       kind=K.GUN, dmg=(18, 26), acc=0.55, rng=380, cooldown=120, price=1900),
    Weapon(id="minigun",   name="מיניגן",          cat=C.HEAVY, art="minigun",  kind=K.GUN, dmg=(12, 18), acc=0.42, rng=320, cooldown=45,  price=3200),
    Weapon(id="browning",  name="בראונינג",        cat=C.HEAVY, art="mg_heavy", kind=K.GUN, dmg=(24, 34), acc=0.48, rng=400, cooldown=140, price=2400),
    Weapon(id="barrett_mg", name="בארט כבד",        cat=C.HEAVY, art="mg_heavy", kind=K.GUN, dmg=(30, 42), acc=0.50, rng=420, cooldown=200, price=2800),

    # ----- נשק קר -----
    Weapon(id="dagger",    name="פגיון",           cat=C.COLD, art="dagger",   kind=K.MELEE, dmg=(14, 22), acc=1.0,  rng=36,  cooldown=330, price=60),
    Weapon(id="sword",     name="חרב",             cat=C.COLD, art="sword",    kind=K.MELEE, dmg=(26, 38), acc=1.0,  rng=48,  cooldown=520, price=220),
    Weapon(id="spear",     name="חנית",            cat=C.COLD, art="spear",    kind=K.MELEE, dmg=(22, 32), acc=1.0,  rng=66,  cooldown=620, price=260),
    Weapon(id="bow",       name="קשת",             cat=C.COLD, art="bow",      kind=K.GUN,   dmg=(24, 34), acc=0.80, rng=380, cooldown=700, price=300, speed=7, ammo="ammo_arrow"),
    Weapon(id="slingshot", name="רוגטקה",          cat=C.COLD, art="sling",    kind=K.GUN,   dmg=(8, 14),  acc=0.60, rng=240, cooldown=450, price=40,  speed=6),
    Weapon(id="shuriken",  name="שוריקנים",        cat=C.COLD, art="shuriken", kind=K.GUN,   dmg=(12, 18), acc=0.72, rng=260, cooldown=260, price=180, speed=8),

    # ----- רימונים (נקנים ביחידות) -----
    Weapon(id="grenade",   name="רימון יד",        cat=C.GRENADES, art="grenade", kind=K.THROW, dmg=(45, 70), acc=1.0, rng=220, cooldown=800, price=90,  radius=72),
    Weapon(id="smoke",     name="רימון עשן",       cat=C.GRENADES, art="smoke",   kind=K.THROW, dmg=(0, 0),   acc=1.0, rng=220, cooldown=800, price=60,  radius=96),
]
