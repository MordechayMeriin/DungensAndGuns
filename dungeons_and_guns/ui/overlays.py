# -*- coding: utf-8 -*-
"""חלונות קטנים מעל המשחק: פרטי אויב, ומסך "נגמרו החיים"."""

import pygame

from ..config import SCREEN_H, SCREEN_W
from ..models import GameState
from . import colors
from .canvas import Canvas
from .world_view import WorldView


def draw_inspect(canvas: Canvas, world: WorldView, state: GameState) -> None:
    """תיבה מעל האויב שלחצו עליו: איזה נשק יש לו וכמה חיים נשארו."""
    e = state.level.enemy_by_uid(state.inspect_uid)
    if e is None or state.inspect_until < state.now:
        return
    w, font = e.weapon, canvas.font_small
    lines = [
        canvas.text(font, "%s - %s" % (w.name, w.cat), (255, 226, 150)),
        canvas.text(font, "נזק %d-%d | דיוק %d%% | טווח %d" % (
            w.dmg[0], w.dmg[1], round(w.acc * 100), w.rng), colors.TEXT),
        canvas.text(font, "חיים: %d/%d" % (round(e.hp), e.max_hp), (255, 168, 168)),
    ]
    width = max(t.get_width() for t in lines) + 110 + 30
    height = 76
    bx = max(6, min(SCREEN_W - width - 6, world.sx(e.x) - width // 2))
    by = max(40, world.sy(e.y) - e.r - height - 10)
    box = pygame.Rect(bx, by, width, height)
    pygame.draw.rect(canvas.screen, (26, 26, 32), box, border_radius=7)
    pygame.draw.rect(canvas.screen, (198, 92, 92), box, 2, border_radius=7)
    canvas.item_icon(pygame.Rect(box.x + 10, box.y + 18, 110, 40), w)
    for i, text in enumerate(lines):
        canvas.screen.blit(text, (box.right - 10 - text.get_width(), box.y + 12 + i * 17))


def draw_game_over(canvas: Canvas, state: GameState) -> None:
    canvas.dim(220)
    canvas.blit_centered_x(canvas.text(canvas.font_big, "נגמרו החיים", (230, 60, 60)), SCREEN_H // 2 - 60)
    canvas.blit_centered_x(canvas.text(canvas.font, "הגעת לשלב %d" % state.level.number, colors.TEXT),
                           SCREEN_H // 2)
    canvas.blit_centered_x(canvas.text(canvas.font, "לחץ R כדי להתחיל מחדש", (160, 220, 160)),
                           SCREEN_H // 2 + 40)
