# -*- coding: utf-8 -*-
"""כל סוגי המשאבים במפה. כל משאב נאסף פעם אחת ונעלם (renew=0).
מכרה זהב ומכרה יהלום לא נותנים מטבעות - המטיל והיהלום עצמם הם כסף (100 ו-1000 מטבעות).
renew = אם רוצים שמשאב יחזור: אחרי כמה מילישניות.
drops = החומרים שמקבלים לתיק בכל איסוף, food = אוכל שמקבלים (בשר מהחיות)."""

from ..models import ResourceKind as R
from ..models import ResourceType

RESOURCE_TYPES = [
    ResourceType(kind=R.TREE,    name="עץ", drops=("log",), food=None, tool="saw",     value=(6, 11),   color=(58, 157, 58),   mark="עץ", renew=0,     weight=10),
    ResourceType(kind=R.BRICKS,  name="מכרה לבנים", drops=("brick",), food=None, tool="pickaxe", value=(4, 8),    color=(168, 86, 62),   mark="לב", renew=0,     weight=8),
    ResourceType(kind=R.COPPER,  name="מכרה נחושת", drops=("copper",), food=None, tool="pickaxe", value=(8, 15),   color=(205, 118, 58),  mark="נח", renew=0,     weight=8),
    ResourceType(kind=R.IRON,    name="מכרה ברזל", drops=("iron",), food=None, tool="pickaxe", value=(12, 20),  color=(172, 176, 186), mark="בר", renew=0,     weight=7),
    ResourceType(kind=R.GAS,     name="באר גז", drops=("gas",), food=None, tool="pickaxe", value=(20, 32),  color=(150, 112, 206), mark="גז", renew=0,     weight=5),
    ResourceType(kind=R.GOLD,    name="מכרה זהב", drops=("gold",), food=None, tool="pickaxe", value=(0, 0),    color=(228, 186, 54),  mark="זה", renew=0,     weight=4),
    ResourceType(kind=R.DIAMOND, name="מכרה יהלום", drops=("diamond",), food=None, tool="pickaxe", value=(0, 0),    color=(120, 226, 232), mark="יה", renew=0,     weight=2),
    ResourceType(kind=R.WHEAT,   name="שדה חיטה", drops=("wheat",), food=None, tool="sickle",  value=(5, 9),    color=(222, 194, 88),  mark="חי", renew=0, weight=8),
    ResourceType(kind=R.COTTON,  name="שדה כותנה", drops=("cotton",), food=None, tool="sickle",  value=(7, 13),   color=(238, 238, 228), mark="כו", renew=0, weight=7),
    ResourceType(kind=R.COW,     name="פרה", drops=("milk", "leather", "bone"), food="raw_meat", tool=None,      value=(14, 22),  color=(206, 176, 150), mark="פר", renew=0, weight=5),
    ResourceType(kind=R.SHEEP,   name="כבשה", drops=("wool", "bone"), food="raw_meat", tool=None,      value=(11, 18),  color=(226, 226, 214), mark="כב", renew=0, weight=5),
    ResourceType(kind=R.CHICKEN, name="תרנגולת", drops=("egg",), food="raw_meat", tool=None,      value=(7, 12),   color=(214, 120, 112), mark="תר", renew=0, weight=6),
    ResourceType(kind=R.CAVE,    name="מערה", drops=(), food=None, tool="torch",   value=(30, 80),  color=(88, 88, 104),   mark="מע", renew=0,     weight=3),
    ResourceType(kind=R.VOLCANO, name="הר געש רדום", drops=("lava",), food=None, tool="pickaxe", value=(60, 120), color=(196, 64, 40),   mark="הר", renew=0,     weight=2),
]
