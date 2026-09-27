# -*- coding: utf-8 -*-
"""מסך תפריט: רשימת כפתורים שבוחרים בחצים+Enter או בעכבר.

The same widget draws the main menu and the save/load slot picker; the app decides
which options to show and what each one does.
"""

import pygame
from pydantic import BaseModel, ConfigDict

from ..config import SCREEN_H, SCREEN_W, TITLE
from . import colors
from .canvas import Canvas

BUTTON_W, BUTTON_H, BUTTON_GAP = 420, 52, 14


class MenuOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    label: str
    detail: str = ""            # שורה קטנה מתחת (למשל: "שלב 3 | כסף 250")
    enabled: bool = True


class MenuView:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.title = TITLE
        self.subtitle = ""
        self.options: list[MenuOption] = []
        self.selected = 0
        self.status = ""            # הודעה בתחתית (למשל: "הקובץ פגום")
        self._rects: list[pygame.Rect] = []

    def show(self, title: str, options: list[MenuOption], subtitle: str = "") -> None:
        self.title, self.subtitle, self.options = title, subtitle, options
        self.selected = next((i for i, o in enumerate(options) if o.enabled), 0)
        self._layout()

    # ---------- קלט ----------
    def move(self, step: int) -> None:
        """חץ למעלה/למטה - מדלג על כפתורים כבויים."""
        for _ in range(len(self.options)):
            self.selected = (self.selected + step) % len(self.options)
            if self.options[self.selected].enabled:
                return

    def current(self) -> MenuOption | None:
        if self.options and self.options[self.selected].enabled:
            return self.options[self.selected]
        return None

    def option_at(self, pos: tuple[int, int]) -> MenuOption | None:
        for i, rect in enumerate(self._rects):
            if rect.collidepoint(pos) and self.options[i].enabled:
                return self.options[i]
        return None

    def hover(self, pos: tuple[int, int]) -> None:
        for i, rect in enumerate(self._rects):
            if rect.collidepoint(pos) and self.options[i].enabled:
                self.selected = i

    # ---------- ציור ----------
    def _layout(self) -> None:
        total = len(self.options) * (BUTTON_H + BUTTON_GAP) - BUTTON_GAP
        top = max(170, SCREEN_H // 2 - total // 2 + 40)
        self._rects = [pygame.Rect(SCREEN_W // 2 - BUTTON_W // 2, top + i * (BUTTON_H + BUTTON_GAP),
                                   BUTTON_W, BUTTON_H) for i in range(len(self.options))]

    def draw(self, over_game: bool) -> None:
        canvas, screen = self.canvas, self.canvas.screen
        if over_game:
            canvas.dim(200)                   # המשחק מאחור, מוחשך
        else:
            screen.fill((20, 20, 24))
        canvas.blit_centered_x(canvas.text(canvas.font_big, self.title, colors.GOLD), 70)
        if self.subtitle:
            canvas.blit_centered_x(canvas.text(canvas.font, self.subtitle, (190, 190, 190)), 122)

        for i, (option, rect) in enumerate(zip(self.options, self._rects)):
            chosen = i == self.selected and option.enabled
            fill = (58, 125, 58) if chosen else ((46, 46, 54) if option.enabled else (34, 34, 38))
            pygame.draw.rect(screen, fill, rect, border_radius=8)
            pygame.draw.rect(screen, colors.GOLD if chosen else colors.PANEL_LINE, rect, 2,
                             border_radius=8)
            text_col = (255, 255, 255) if option.enabled else (110, 110, 118)
            label = canvas.text(canvas.font, option.label, text_col)
            if option.detail:
                detail = canvas.text(canvas.font_small, option.detail,
                                     (220, 220, 220) if option.enabled else (100, 100, 108))
                screen.blit(label, (rect.centerx - label.get_width() // 2, rect.y + 6))
                screen.blit(detail, (rect.centerx - detail.get_width() // 2, rect.y + 30))
            else:
                screen.blit(label, (rect.centerx - label.get_width() // 2,
                                    rect.centery - label.get_height() // 2))

        if self.status:
            canvas.blit_centered_x(canvas.text(canvas.font, self.status, (255, 168, 120)),
                                   SCREEN_H - 70)
        canvas.blit_centered_x(canvas.text(canvas.font_small, "חצים + Enter או עכבר = בחירה   |   Esc = חזרה",
                                           (150, 150, 150)), SCREEN_H - 30)
