# -*- coding: utf-8 -*-
"""התיק (מקש E): כל מה שיש לך בריבועים, ובנפרד ממנו - שורת המספרים.

גוררים דבר מהתיק לשורה כדי לשים אותו שם, גוררים בין משבצות כדי להחליף ביניהן,
וגוררים מהשורה החוצה כדי להוציא ממנה. התיק רק מדווח מה נגרר לאן - ה-app משנה את השורה.
"""

from typing import NamedTuple

import pygame

from ..config import SCREEN_H, SCREEN_W
from ..data import CATALOG
from ..models import GameState, ItemKind, SlotItem
from . import colors
from .canvas import Canvas
from .hud import rank_text
from .slots import (GAP, SLOT, Entry, draw_hotbar, draw_slot, draw_tooltip, hotbar_rects,
                    slot_at, slot_entry)

HELP_LINES = (
    "חצים = תזוזה | רווח = להשתמש במה שנבחר (לירות, לשתות, לאכול) | 1-9, 0, Z/X או גלגלת = לבחור משבצת",
    "Q = איסוף / תיבה / שלב הבא | T = תרופה | F = אוכל | Y = חנות וסדנה | M = קול | Esc = תפריט",
    "גרור מהתיק לשורה כדי לשים שם | גרור מהשורה החוצה כדי להוציא | E לסגירה",
)
TITLE_W = 110           # עמודת שמות הקבוצות, מימין


class Group(NamedTuple):
    title: str
    entries: list[Entry]


class Drop(NamedTuple):
    """מה קרה כשעזבו את העכבר: איזה דבר, מאיזו משבצת (None = מהתיק), לאיזו (None = החוצה)."""

    item: SlotItem
    from_slot: int | None
    to_slot: int | None


def bag_groups(state: GameState) -> list[Group]:
    """כל מה שיש לשחקן, מחולק לקבוצות (קבוצה ריקה לא מופיעה)."""
    inv = state.inventory
    weapons = [slot_entry(state, SlotItem(kind=ItemKind.WEAPON, id=w.id)) for w in CATALOG.weapons
               if w.id in inv.weapons and (not w.is_throwable or inv.throwable_count(w.id) > 0)]
    usable = ([slot_entry(state, SlotItem(kind=ItemKind.POTION, id=p.id))
               for p in CATALOG.potions if inv.potion_count(p.id) > 0]
              + [slot_entry(state, SlotItem(kind=ItemKind.FOOD, id=f.id))
                 for f in CATALOG.foods if inv.food_count(f.id) > 0])
    ammo = [Entry(a.name, str(inv.ammo_count(a.id)), a)
            for a in CATALOG.ammo_types if inv.ammo_count(a.id) > 0]
    materials = [Entry(r.material, str(inv.material_count(r.kind)), art="mat_%s" % r.kind)
                 for r in CATALOG.resources if r.material and inv.material_count(r.kind) > 0]
    owned = ([Entry(CATALOG.key.name, str(inv.keys), CATALOG.key)] if inv.keys else [])
    owned += ([Entry(t.name, "", t) for t in CATALOG.tools if t.id in inv.tools]
             + [Entry(g.name, "", g) for g in CATALOG.gear if g.id in inv.gear])
    groups = [Group("נשק", weapons), Group("תרופות ואוכל", usable), Group("תחמושת", ammo),
              Group("חומרים", materials), Group("כלים וציוד", owned)]
    return [g for g in groups if g.entries]


class BagView:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.open = False
        self.scroll = 0
        self.max_scroll = 0
        self.panel = pygame.Rect(50, 22, SCREEN_W - 100, SCREEN_H - 44)
        help_top = self.panel.bottom - 12 - 19 * len(HELP_LINES)
        self.hotbar = hotbar_rects(help_top - 10 - SLOT, self.panel.centerx)
        self.grid_clip = pygame.Rect(self.panel.x + 10, self.panel.y + 80,
                                     self.panel.w - 20, self.hotbar[0].y - 40 - self.panel.y - 80)
        self.cells: list[tuple[pygame.Rect, Entry]] = []    # מה צויר בפריים האחרון (לעכבר)
        self.drag: tuple[SlotItem, int | None] | None = None

    def toggle(self) -> None:
        self.open = not self.open
        self.scroll = 0
        self.drag = None

    def scroll_by(self, step: int) -> None:
        self.scroll = max(0, min(self.max_scroll, self.scroll + step))

    # ---------- עכבר ----------
    def _cell_at(self, pos: tuple[int, int]) -> Entry | None:
        if not self.grid_clip.collidepoint(pos):
            return None
        return next((entry for rect, entry in self.cells if rect.collidepoint(pos)), None)

    def press(self, state: GameState, pos: tuple[int, int]) -> None:
        """התחלת גרירה - מהתיק או ממשבצת בשורה."""
        slot = slot_at(self.hotbar, pos)
        if slot is not None:
            item = state.inventory.hotbar[slot]
            if item is not None:
                self.drag = (item, slot)
            return
        entry = self._cell_at(pos)
        if entry is not None and entry.slot_item is not None:
            self.drag = (entry.slot_item, None)

    def release(self, pos: tuple[int, int]) -> Drop | None:
        if self.drag is None:
            return None
        item, from_slot = self.drag
        self.drag = None
        return Drop(item=item, from_slot=from_slot, to_slot=slot_at(self.hotbar, pos))

    # ---------- ציור ----------
    def draw(self, state: GameState, mouse: tuple[int, int]) -> None:
        canvas, screen, panel = self.canvas, self.canvas.screen, self.panel
        canvas.dim(200)
        pygame.draw.rect(screen, colors.PANEL, panel, border_radius=10)
        pygame.draw.rect(screen, colors.PANEL_LINE, panel, 2, border_radius=10)
        canvas.blit_centered_x(canvas.text(canvas.font_big, "התיק", (255, 204, 102)),
                               panel.y + 8, panel.centerx)
        info = "כסף: %d   |   שלב: %d   |   %s" % (
            state.inventory.money, state.level.number, rank_text(state))
        canvas.blit_centered_x(canvas.text(canvas.font_small, info, (200, 200, 200)),
                               panel.y + 52, panel.centerx)

        hover = self._draw_grid(state, mouse)

        label = canvas.text(canvas.font_small, "שורת המספרים (1-9, 0)", (255, 204, 102))
        screen.blit(label, (self.hotbar[-1].right - label.get_width(), self.hotbar[0].y - 22))
        hover_slot = slot_at(self.hotbar, mouse)
        dragging_from = self.drag[1] if self.drag else None
        draw_hotbar(canvas, state, self.hotbar, hover=hover_slot, hidden=dragging_from)
        if hover_slot is not None and hover is None and hover_slot != dragging_from:
            item = state.inventory.hotbar[hover_slot]
            if item is not None:
                hover = slot_entry(state, item)

        y = self.hotbar[0].bottom + 10
        for line in HELP_LINES:
            canvas.blit_centered_x(canvas.text(canvas.font_small, line, (150, 150, 160)), y,
                                   panel.centerx)
            y += 19

        if self.drag is not None:
            entry = slot_entry(state, self.drag[0])
            icon = canvas.icons.square(entry.item, SLOT - 10, entry.art)
            screen.blit(icon, (mouse[0] - icon.get_width() // 2, mouse[1] - icon.get_height() // 2))
        elif hover is not None:
            draw_tooltip(canvas, "%s (%s)" % (hover.name, hover.count) if hover.count else hover.name,
                         mouse)

    def _draw_grid(self, state: GameState, mouse: tuple[int, int]) -> Entry | None:
        """כל קבוצה בשורה משלה: השם מימין והריבועים משמאלו. מחזיר על מה העכבר עומד."""
        canvas, screen, clip = self.canvas, self.canvas.screen, self.grid_clip
        right = clip.right - TITLE_W
        per_row = max(1, (right - clip.x + GAP) // (SLOT + GAP))
        self.cells = []
        hover = None
        y = clip.y - self.scroll
        screen.set_clip(clip)
        for group in bag_groups(state):
            title = canvas.text(canvas.font, group.title, (255, 204, 102))
            screen.blit(title, (clip.right - 4 - title.get_width(), y + SLOT // 2 - title.get_height() // 2))
            for i, entry in enumerate(group.entries):
                row, col = divmod(i, per_row)
                rect = pygame.Rect(right - (col + 1) * (SLOT + GAP) + GAP,
                                   y + row * (SLOT + GAP), SLOT, SLOT)
                over = clip.collidepoint(mouse) and rect.collidepoint(mouse)
                draw_slot(canvas, rect, entry, hover=over)
                self.cells.append((rect, entry))
                if over:
                    hover = entry
            rows = (len(group.entries) + per_row - 1) // per_row
            y += rows * (SLOT + GAP) + 8
        screen.set_clip(None)
        self.max_scroll = max(0, y + self.scroll - clip.bottom)
        self.scroll = min(self.scroll, self.max_scroll)
        if self.scroll < self.max_scroll:
            more = canvas.text(canvas.font_small, "יש עוד למטה - גלגלת העכבר", (150, 150, 160))
            screen.blit(more, (clip.x, clip.bottom - more.get_height()))
        return hover
