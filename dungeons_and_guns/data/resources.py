# -*- coding: utf-8 -*-
"""כל סוגי המשאבים במפה. renew = אחרי כמה מילישניות המשאב חוזר (0 = נעלם לתמיד).
material = הפריט שמקבלים לתיק בכל איסוף (חוץ מהכסף)."""

from ..models import ResourceKind as R
from ..models import ResourceType

RESOURCE_TYPES = [
    ResourceType(kind=R.TREE,    name="עץ",          material="בול עץ",      tool="saw",     value=(6, 11),   color=(58, 157, 58),   mark="עץ", renew=0,     weight=10),
    ResourceType(kind=R.BRICKS,  name="מכרה לבנים",  material="לבנה",        tool="pickaxe", value=(4, 8),    color=(168, 86, 62),   mark="לב", renew=0,     weight=8),
    ResourceType(kind=R.COPPER,  name="מכרה נחושת",  material="מטיל נחושת",  tool="pickaxe", value=(8, 15),   color=(205, 118, 58),  mark="נח", renew=0,     weight=8),
    ResourceType(kind=R.IRON,    name="מכרה ברזל",   material="מטיל ברזל",   tool="pickaxe", value=(12, 20),  color=(172, 176, 186), mark="בר", renew=0,     weight=7),
    ResourceType(kind=R.GAS,     name="באר גז",      material="מיכל גז",     tool="pickaxe", value=(20, 32),  color=(150, 112, 206), mark="גז", renew=0,     weight=5),
    ResourceType(kind=R.GOLD,    name="מכרה זהב",    material="מטיל זהב",    tool="pickaxe", value=(34, 52),  color=(228, 186, 54),  mark="זה", renew=0,     weight=4),
    ResourceType(kind=R.DIAMOND, name="מכרה יהלום",  material="יהלום",       tool="pickaxe", value=(60, 95),  color=(120, 226, 232), mark="יה", renew=0,     weight=2),
    ResourceType(kind=R.WHEAT,   name="שדה חיטה",    material="שק חיטה",     tool="sickle",  value=(5, 9),    color=(222, 194, 88),  mark="חי", renew=12000, weight=8),
    ResourceType(kind=R.COTTON,  name="שדה כותנה",   material="צרור כותנה",  tool="sickle",  value=(7, 13),   color=(238, 238, 228), mark="כו", renew=12000, weight=7),
    ResourceType(kind=R.COW,     name="פרה",         material="בקבוק חלב",   tool=None,      value=(14, 22),  color=(206, 176, 150), mark="פר", renew=15000, weight=5),
    ResourceType(kind=R.SHEEP,   name="כבשה",        material="צמר",         tool=None,      value=(11, 18),  color=(226, 226, 214), mark="כב", renew=15000, weight=5),
    ResourceType(kind=R.CHICKEN, name="תרנגולת",     material="ביצה",        tool=None,      value=(7, 12),   color=(214, 120, 112), mark="תר", renew=10000, weight=6),
    ResourceType(kind=R.CAVE,    name="מערה",        material=None,          tool="torch",   value=(30, 80),  color=(88, 88, 104),   mark="מע", renew=0,     weight=3),
    ResourceType(kind=R.VOLCANO, name="הר געש רדום", material="אבן געש",     tool="pickaxe", value=(60, 120), color=(196, 64, 40),   mark="הר", renew=0,     weight=2),
]
