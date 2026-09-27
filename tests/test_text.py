# -*- coding: utf-8 -*-
from dungeons_and_guns.ui.text import rtl


def test_rtl_keeps_numbers_and_times_readable():
    assert rtl("שלב 3 | 27/09 13:04").startswith("27/09 13:04 | 3 ")
    assert rtl("חיים: 100/100") == "100/100 :םייח"
