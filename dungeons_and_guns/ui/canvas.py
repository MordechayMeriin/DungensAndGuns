# -*- coding: utf-8 -*-
"""המשטח שעליו מציירים, עם הגופנים, התמונות וכמה פעולות ציור נפוצות."""

import pygame

from ..config import SCREEN_H, SCREEN_W
from ..models import ItemBase
from .icons import IconCache
from .text import load_font, rtl


class Canvas:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = load_font(18)
        self.font_small = load_font(14)
        self.font_big = load_font(34, bold=True)
        self.icons = IconCache()

    def text(self, font: pygame.font.Font, text: str, color) -> pygame.Surface:
        """מכין טקסט עברי לציור (מימין לשמאל)."""
        return font.render(rtl(text), True, color)

    def blit_centered_x(self, surface: pygame.Surface, y: int, cx: int = SCREEN_W // 2) -> None:
        self.screen.blit(surface, (cx - surface.get_width() // 2, y))

    def dim(self, alpha: int) -> None:
        """מחשיך את כל המסך (מתחת לחלונות כמו חנות וגלגל)."""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def bar(self, cx: int, y: int, w: int, ratio: float, color) -> None:
        """קו חיים קטן מעל דמות."""
        ratio = max(0.0, min(1.0, ratio))
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(cx - w // 2 - 1, y - 1, w + 2, 7))
        pygame.draw.rect(self.screen, (55, 55, 55), pygame.Rect(cx - w // 2, y, w, 5))
        pygame.draw.rect(self.screen, color, pygame.Rect(cx - w // 2, y, int(w * ratio), 5))

    def item_icon(self, rect: pygame.Rect, item: ItemBase) -> None:
        pygame.draw.rect(self.screen, (24, 24, 28), rect, border_radius=4)
        self.screen.blit(self.icons.get(item, (rect.w, rect.h)), rect.topleft)
