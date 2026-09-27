# -*- coding: utf-8 -*-
"""הגדרות כלליות של המשחק."""

import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# תיקיית התצלומים האמיתיים. אם קובץ חסר - המשחק מצייר את הפריט בעצמו.
IMAGE_DIR = os.path.join(ROOT_DIR, "images")
# משחקים שמורים
SAVE_DIR = os.path.join(ROOT_DIR, "saves")

TILE = 32
SCREEN_W, SCREEN_H = 960, 640
FPS = 60
TITLE = "מבוך ונשק"
