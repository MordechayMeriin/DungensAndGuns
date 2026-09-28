# -*- coding: utf-8 -*-
"""הדרגות. על כל אויב שמחסלים מקבלים נקודות (על אויב עם נשק טוב יותר - יותר נקודות),
וכל דרגה פותחת בחנות כמה כלי נשק מאותה מחלקה, מהחלש לחזק.
נשק שלא כתוב כאן (אקדחים, שוטגן, נשק קר, רימונים) פתוח מההתחלה.
"""

from ..models import Rank

RANKS = [
    Rank(name="טוראי",   points=0),
    # תתי מקלע
    Rank(name='רב"ט',    points=40,   unlocks=("uzi", "mac10")),
    Rank(name="סמל",     points=100,  unlocks=("mp5", "mp7")),
    # רובי סער
    Rank(name='סמ"ר',    points=180,  unlocks=("m16", "type56", "m16a1", "ak47", "aks47")),
    Rank(name='רס"ל',    points=280,  unlocks=("m16a2", "m4", "m16a3", "akm", "akms")),
    Rank(name='רס"ר',    points=400,  unlocks=("m16a4", "m4a1", "m4a2", "m4a3", "m4a4", "tavor")),
    # רובי צלפים
    Rank(name='רס"מ',    points=550,  unlocks=("barak", "dragunov", "remington")),
    Rank(name='רס"ב',    points=720,  unlocks=("tango51", "blaser", "barrett82")),
    # מקלעים כבדים
    Rank(name="סגן",     points=920,  unlocks=("mag", "browning")),
    Rank(name="סרן",     points=1150, unlocks=("barrett_mg", "minigun")),
    Rank(name="רב סרן",  points=1500),
]
