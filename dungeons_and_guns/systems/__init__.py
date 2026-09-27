# -*- coding: utf-8 -*-
"""חוקי המשחק. כל פונקציה כאן מקבלת GameState ומשנה אותו - בלי pygame ובלי ציור.

Systems talk back to the player only through ``state.say(...)`` / ``state.play(...)``;
the app turns those into on-screen text and sounds.
"""
