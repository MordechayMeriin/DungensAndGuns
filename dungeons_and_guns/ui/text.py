# -*- coding: utf-8 -*-
"""טקסט בעברית: גופנים וסידור מימין לשמאל."""

import os
import re

import pygame

# רצף של אנגלית/מספרים שלא הופכים (כולל שעות כמו 13:04)
_LATIN_CHAR = r"(?:[A-Za-z0-9\-\./+%]|(?<=\d):(?=\d))"
LATIN_RUN = re.compile(r"[A-Za-z0-9]%s*(?: %s+)*" % (_LATIN_CHAR, _LATIN_CHAR))
MIRRORED = {"(": ")", ")": "(", "[": "]", "]": "[", "{": "}", "}": "{", "<": ">", ">": "<"}


def rtl(text: str) -> str:
    """מסדר טקסט עברי לתצוגה מימין לשמאל, בלי להפוך מספרים ומילים באנגלית."""
    parts = []
    idx = 0
    for match in LATIN_RUN.finditer(text):
        if match.start() > idx:
            parts.append(("he", text[idx:match.start()]))
        parts.append(("latin", match.group()))
        idx = match.end()
    if idx < len(text):
        parts.append(("he", text[idx:]))
    return "".join(s if kind == "latin" else "".join(MIRRORED.get(c, c) for c in reversed(s))
                   for kind, s in reversed(parts))


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    for path in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\tahoma.ttf"):
        if os.path.exists(path):
            font = pygame.font.Font(path, size)
            font.set_bold(bold)
            return font
    return pygame.font.SysFont("arial", size, bold=bold)
