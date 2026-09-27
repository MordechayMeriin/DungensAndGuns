# -*- coding: utf-8 -*-
"""לוח ציור מוגדל לציורי הפריטים, וצבעי הבסיס שלהם.

כל ציור מצויר על לוח של 88x32 (הגובה נמדד מהמרכז: -16 למעלה, +16 למטה),
בהגדלה של פי 4, ואז מוקטן - ככה הקווים יוצאים חלקים והנשק נראה אמיתי.
"""

import pygame

ICON_W, ICON_H, ICON_SCALE = 88, 32, 4

STEEL = (186, 190, 202)
STEEL_HI = (224, 228, 238)
STEEL_LO = (126, 130, 142)
GUNMETAL = (108, 112, 124)
BLACK = (52, 54, 60)
BLACK_HI = (76, 78, 86)
BLACK_LO = (32, 32, 38)
POLYMER = (64, 64, 72)
WOOD = (146, 96, 48)
WOOD_HI = (182, 128, 70)
WOOD_LO = (104, 66, 30)
OLIVE = (94, 104, 70)
OLIVE_HI = (124, 134, 92)
TAN = (176, 150, 96)
LENS = (118, 172, 150)


class IconPainter:
    """מצייר על לוח מוגדל, בקואורדינטות של הלוח הקטן (88x32)."""

    def __init__(self, surface, scale):
        self.surf = surface
        self.k = scale
        self.cy = surface.get_height() / 2.0

    def _pt(self, a, b):
        return (int(round(a * self.k)), int(round(self.cy + b * self.k)))

    def _len(self, v):
        return max(1, int(round(v * self.k)))

    def box(self, a, b, w, h, col, rad=0):
        rect = pygame.Rect(self._pt(a, b), (self._len(w), self._len(h)))
        pygame.draw.rect(self.surf, col, rect, border_radius=int(round(rad * self.k)))

    def poly(self, points, col):
        pygame.draw.polygon(self.surf, col, [self._pt(a, b) for a, b in points])

    def line(self, a1, b1, a2, b2, col, w=1):
        pygame.draw.line(self.surf, col, self._pt(a1, b1), self._pt(a2, b2), self._len(w))

    def circ(self, a, b, r, col, w=0):
        pygame.draw.circle(self.surf, col, self._pt(a, b), self._len(r),
                           0 if w == 0 else self._len(w))

    def arc(self, a, b, w, h, start, end, col, width=1):
        rect = pygame.Rect(self._pt(a, b), (self._len(w), self._len(h)))
        pygame.draw.arc(self.surf, col, rect, start, end, self._len(width))

    def ribs(self, a, b, count, step, height, col, w=0.7):
        for i in range(count):
            self.line(a + i * step, b, a + i * step, b + height, col, w)
