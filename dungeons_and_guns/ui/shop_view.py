# -*- coding: utf-8 -*-
"""חלון החנות: רשימה נגללת של פריטים עם כפתור קנייה לכל אחד."""

import pygame

from ..config import SCREEN_H, SCREEN_W
from ..data import CATALOG
from ..models import GameState, WeaponKind
from ..systems.shop import ShopKind, ShopRow, shop_sections
from . import colors
from .canvas import Canvas

SCROLL_KEYS = {pygame.K_UP: -60, pygame.K_DOWN: 60, pygame.K_PAGEUP: -420,
               pygame.K_PAGEDOWN: 420, pygame.K_HOME: -99999, pygame.K_END: 99999}


def row_label(state: GameState, row: ShopRow) -> str:
    inv, item = state.inventory, row.item
    match row.kind:
        case ShopKind.WEAPON:
            if item.kind == WeaponKind.MELEE:
                return "%s   נזק %d-%d | מכה מקרוב | בלי תחמושת" % (item.name, *item.dmg)
            ammo = CATALOG.ammo_for(item)
            extra = " | %s" % ammo.name if ammo else " | בלי תחמושת"
            if item.pellets > 1:
                extra = " | %d כדורים בירייה%s" % (item.pellets, extra)
            return "%s   נזק %d-%d | דיוק %d%% | טווח %d%s" % (
                item.name, item.dmg[0], item.dmg[1], round(item.acc * 100), item.rng, extra)
        case ShopKind.THROWABLE:
            have = inv.throwable_count(item.id)
            if item.id == "smoke":
                return "%s   מסתיר אותך מהאויבים (יש לך %d)" % (item.name, have)
            return "%s   נזק %d-%d בכל הסביבה (יש לך %d)" % (item.name, *item.dmg, have)
        case ShopKind.AMMO:
            return "%s   %s | %d %s בחפיסה (יש לך %d)" % (
                item.name, item.desc, item.pack, item.unit, inv.ammo_count(item.id))
        case ShopKind.POTION:
            return "%s   מחזירה %d חיים (יש לך %d)" % (
                item.name, item.heal, inv.potion_count(item.id))
        case _:
            return "%s   %s" % (item.name, item.desc)


class ShopView:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.open = False
        self.scroll = 0
        self.max_scroll = 0
        self.buttons: list[tuple[pygame.Rect, ShopRow]] = []

    def toggle(self) -> None:
        self.open = not self.open
        self.scroll = 0

    def scroll_by(self, step: int) -> None:
        self.scroll = max(0, min(self.max_scroll, self.scroll + step))

    def row_at(self, pos: tuple[int, int]) -> ShopRow | None:
        """על איזה כפתור קנייה לחצו (אם בכלל)."""
        return next((row for rect, row in self.buttons if rect.collidepoint(pos)), None)

    def draw(self, state: GameState) -> None:
        canvas, screen = self.canvas, self.canvas.screen
        money = state.inventory.money
        panel = pygame.Rect(80, 40, SCREEN_W - 160, SCREEN_H - 80)
        canvas.dim(210)
        pygame.draw.rect(screen, colors.PANEL, panel, border_radius=10)
        pygame.draw.rect(screen, colors.PANEL_LINE, panel, 2, border_radius=10)

        canvas.blit_centered_x(canvas.text(canvas.font_big, "החנות", (255, 204, 102)),
                               panel.y + 10, panel.centerx)
        canvas.blit_centered_x(canvas.text(
            canvas.font_small, "כסף: %d   |   גלגלת עכבר או חצים לגלילה   |   Y לסגירה" % money,
            (180, 180, 180)), panel.y + 54, panel.centerx)

        self.buttons = []
        y = panel.y + 84 - self.scroll
        clip = pygame.Rect(panel.x + 8, panel.y + 78, panel.w - 16, panel.h - 90)
        screen.set_clip(clip)
        for section in shop_sections(state):
            if clip.y - 46 < y < clip.bottom:
                text = canvas.text(canvas.font, section.title, (255, 204, 102))
                screen.blit(text, (panel.right - 24 - text.get_width(), y))
            y += 30
            for row in section.rows:
                if clip.y - 46 < y < clip.bottom:
                    self._draw_row(state, row, pygame.Rect(panel.x + 24, y, panel.w - 48, 46))
                y += 48
        screen.set_clip(None)
        self.max_scroll = max(0, y + self.scroll - panel.bottom + 40)

    def _draw_row(self, state: GameState, row: ShopRow, rect: pygame.Rect) -> None:
        canvas, screen, item = self.canvas, self.canvas.screen, row.item
        pygame.draw.rect(screen, (42, 42, 48), rect, border_radius=6)
        text = canvas.text(canvas.font_small, row_label(state, row), colors.TEXT)
        screen.blit(text, (rect.right - 10 - text.get_width(), rect.y + 15))

        btn = pygame.Rect(rect.x + 8, rect.y + 12, 110, 22)
        if row.owned:
            color, label = (85, 85, 85), "נרכש"
        elif state.inventory.money >= item.price:
            color, label = (58, 125, 58), "קנה %d" % item.price
        else:
            color, label = (90, 60, 60), "%d כסף" % item.price
        pygame.draw.rect(screen, color, btn, border_radius=5)
        btext = canvas.text(canvas.font_small, label, (255, 255, 255))
        screen.blit(btext, (btn.centerx - btext.get_width() // 2, btn.y + 3))
        canvas.item_icon(pygame.Rect(btn.right + 12, rect.y + 3, 110, 40), item)
        if not row.owned:
            self.buttons.append((btn.copy(), row))
