# -*- coding: utf-8 -*-
from dungeons_and_guns.ui.text import rtl


def test_rtl_keeps_numbers_and_times_readable():
    assert rtl("שלב 3 | 27/09 13:04").startswith("27/09 13:04 | 3 ")
    assert rtl("חיים: 100/100") == "100/100 :םייח"


def test_all_ui_modules_import():
    """שגיאת כתיב בקובץ ציור (למשל מירכאות בתוך טקסט) נתפסת כאן ולא רק כשמפעילים את המשחק."""
    import importlib
    import pkgutil

    import dungeons_and_guns.ui as ui
    for module in pkgutil.walk_packages(ui.__path__, ui.__name__ + "."):
        importlib.import_module(module.name)
    importlib.import_module("dungeons_and_guns.app")
