# -*- coding: utf-8 -*-
"""כל החומרים שאוספים מהמשאבים. מטיל זהב ויהלום הם גם כסף (100 ו-1000 מטבעות)."""

from ..models import Material

MATERIALS = [
    Material(id="log",     name="בול עץ",      art="mat_tree"),
    Material(id="brick",   name="לבנה",        art="mat_bricks"),
    Material(id="copper",  name="מטיל נחושת",  art="mat_copper"),
    Material(id="iron",    name="מטיל ברזל",   art="mat_iron"),
    Material(id="gas",     name="מיכל גז",     art="mat_gas"),
    Material(id="gold",    name="מטיל זהב",    art="mat_gold"),
    Material(id="diamond", name="יהלום",       art="mat_diamond"),
    Material(id="wheat",   name="שק חיטה",     art="mat_wheat"),
    Material(id="cotton",  name="צרור כותנה",  art="mat_cotton"),
    Material(id="milk",    name="בקבוק חלב",   art="mat_cow"),
    Material(id="egg",     name="ביצה",        art="mat_chicken"),
    Material(id="wool",    name="צמר",         art="mat_sheep"),
    Material(id="leather", name="עור",         art="mat_leather"),
    Material(id="bone",    name="עצם",         art="mat_bone"),
    Material(id="lava",    name="אבן געש",     art="mat_volcano"),
]
