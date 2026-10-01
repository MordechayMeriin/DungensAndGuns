# -*- coding: utf-8 -*-
"""חלונות קטנים מעל המשחק: פרטי אויב, ומסך "נגמרו החיים"."""

import pygame

from ..config import SCREEN_H, SCREEN_W
from ..data import CATALOG
from ..models import GameState
from . import colors
from .canvas import Canvas
from .world_view import WorldView


ICON = 30


def draw_inspect(canvas: Canvas, world: WorldView, state: GameState) -> None:
    """תיבה מעל האויב שלחצו עליו: הנשק, החיים, הציוד והרימונים שלו."""
    e = state.level.enemy_by_uid(state.inspect_uid)
    if e is None or state.inspect_until < state.now:
        return
    w, font = e.weapon, canvas.font_small
    gear = [g for g in CATALOG.gear if g.id in e.gear]
    grenades = [(CATALOG.weapon(wid), n) for wid, n in e.grenades.items() if n > 0]
    texts = [
        ("%s - %s" % (w.name, w.cat), (255, 226, 150)),
        ("נזק %d-%d | דיוק %d%% | טווח %d" % (w.dmg[0], w.dmg[1], round(w.acc * 100), w.rng),
         colors.TEXT),
        ("חיים: %d/%d" % (round(e.hp), e.max_hp), (255, 168, 168)),
        ("ציוד: %s" % (", ".join(g.name for g in gear) if gear else "אין"), (170, 210, 255)),
        ("רימונים: %s" % (", ".join("%s x%d" % (g.name, n) for g, n in grenades) if grenades else "אין"),
         (170, 230, 150)),
    ]
    lines = [canvas.text(font, text, color) for text, color in texts]
    icons = [g for g in gear] + [g for g, _ in grenades]
    width = max(max(t.get_width() for t in lines) + 110 + 30, len(icons) * (ICON + 4) + 20)
    height = 14 + 17 * len(lines) + (ICON + 8 if icons else 0)
    bx = max(6, min(SCREEN_W - width - 6, world.sx(e.x) - width // 2))
    by = max(40, world.sy(e.y) - e.r - height - 10)
    box = pygame.Rect(bx, by, width, height)
    pygame.draw.rect(canvas.screen, (26, 26, 32), box, border_radius=7)
    pygame.draw.rect(canvas.screen, (198, 92, 92), box, 2, border_radius=7)
    canvas.item_icon(pygame.Rect(box.x + 10, box.y + 14, 110, 40), w)
    for i, text in enumerate(lines):
        canvas.screen.blit(text, (box.right - 10 - text.get_width(), box.y + 8 + i * 17))
    y = box.y + 12 + 17 * len(lines)
    for i, item in enumerate(icons):
        rect = pygame.Rect(box.right - 10 - (i + 1) * (ICON + 4) + 4, y, ICON, ICON)
        pygame.draw.rect(canvas.screen, (44, 44, 52), rect, border_radius=4)
        canvas.screen.blit(canvas.icons.square(item, ICON - 4), (rect.x + 2, rect.y + 2))


def draw_game_over(canvas: Canvas, state: GameState) -> None:
    canvas.dim(220)
    canvas.blit_centered_x(canvas.text(canvas.font_big, "נגמרו החיים", (230, 60, 60)), SCREEN_H // 2 - 60)
    canvas.blit_centered_x(canvas.text(canvas.font, "הגעת לשלב %d" % state.level.number, colors.TEXT),
                           SCREEN_H // 2)
    canvas.blit_centered_x(canvas.text(canvas.font, "לחץ R כדי להתחיל מחדש", (160, 220, 160)),
                           SCREEN_H // 2 + 40)
