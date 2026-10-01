# -*- coding: utf-8 -*-
"""מה רואים בזמן המשחק: חיים ודרגה למעלה, שורת המספרים למטה, והודעות.

כל השאר (כסף, שלב, חומרים, עזרה על המקשים) נמצא בתיק - מקש E.
"""

import pygame

from ..config import SCREEN_H, SCREEN_W
from ..data import CATALOG
from ..models import GameState
from ..systems import missions
from ..systems.interaction import interact_hint
from ..systems.inventory import current_weapon
from ..systems.ranks import current_rank
from . import colors
from .canvas import Canvas
from .slots import SLOT, draw_hotbar, hotbar_rects

HOTBAR_Y = SCREEN_H - SLOT - 12
HP_BAR_W = 170


def rank_text(state: GameState) -> str:
    """שורת הדרגה: הדרגה עכשיו, וכמה נקודות חסרות לדרגה הבאה."""
    points = state.player.points
    rank, nxt = current_rank(state), CATALOG.next_rank(points)
    if nxt is None:
        return "דרגה: %s | %d נקודות" % (rank.name, points)
    return "דרגה: %s | %d/%d נקודות לדרגת %s" % (rank.name, points, nxt.points, nxt.name)


def game_hotbar_rects() -> list[pygame.Rect]:
    return hotbar_rects(HOTBAR_Y)


def _draw_top_bar(canvas: Canvas, state: GameState) -> None:
    screen, player = canvas.screen, state.player
    pygame.draw.rect(screen, (18, 18, 22), pygame.Rect(0, 0, SCREEN_W, 34))

    color = colors.hp_color(player.hp_ratio)
    text = canvas.text(canvas.font, "חיים: %d/%d" % (round(player.hp), player.max_hp), color)
    x = SCREEN_W - 14 - text.get_width()
    screen.blit(text, (x, 7))
    bar = pygame.Rect(x - 12 - HP_BAR_W, 11, HP_BAR_W, 12)
    pygame.draw.rect(screen, (55, 55, 60), bar, border_radius=4)
    fill = bar.copy()
    fill.w = int(bar.w * max(0.0, min(1.0, player.hp_ratio)))
    pygame.draw.rect(screen, color, fill, border_radius=4)

    screen.blit(canvas.text(canvas.font, rank_text(state), (150, 200, 255)), (14, 7))


def mission_line(state: GameState) -> str:
    mission = state.mission
    if mission is None:
        return ""
    left = missions.time_left(state) // 1000
    count = " (%d/%d)" % (mission.progress, mission.goal) if mission.goal > 1 else ""
    return "משימה: %s%s | נשאר %d:%02d" % (missions.mission_text(mission), count, left // 60, left % 60)


def _draw_mission(canvas: Canvas, state: GameState) -> None:
    line = mission_line(state)
    if not line:
        return
    urgent = missions.time_left(state) < 60_000
    text = canvas.text(canvas.font_small, line, colors.HP_RED if urgent else (255, 214, 102))
    box = pygame.Rect(8, 38, text.get_width() + 14, text.get_height() + 6)
    pygame.draw.rect(canvas.screen, (24, 24, 30), box, border_radius=5)
    canvas.screen.blit(text, (box.x + 7, box.y + 3))


def _label(canvas: Canvas, text: str, pos: tuple[int, int], color) -> None:
    """טקסט קטן עם רקע כהה - שייקרא גם על ערפל."""
    surf = canvas.text(canvas.font_small, text, color)
    box = pygame.Rect(pos[0], pos[1], surf.get_width() + 12, surf.get_height() + 4)
    pygame.draw.rect(canvas.screen, (24, 24, 30), box, border_radius=5)
    canvas.screen.blit(surf, (box.x + 6, box.y + 2))


def _draw_box(canvas: Canvas, text: pygame.Surface, y: int, border=None) -> None:
    box = pygame.Rect(SCREEN_W // 2 - text.get_width() // 2 - 12, y, text.get_width() + 24, 30)
    pygame.draw.rect(canvas.screen, (44, 44, 52), box, border_radius=6)
    if border:
        pygame.draw.rect(canvas.screen, border, box, 1, border_radius=6)
    canvas.screen.blit(text, (box.x + 12, box.y + 5))


def draw_hud(canvas: Canvas, state: GameState) -> None:
    _draw_top_bar(canvas, state)
    _draw_mission(canvas, state)

    rects = game_hotbar_rects()
    draw_hotbar(canvas, state, rects)
    _label(canvas, "E = תיק", (rects[-1].right + 12, HOTBAR_Y + SLOT // 2 - 11), (170, 170, 180))

    item = state.inventory.selected_item
    if item is not None:
        entry_name = CATALOG.item(item.kind, item.id).name
        weapon = current_weapon(state)
        if weapon is not None and weapon.ammo == CATALOG.poison.ammo and state.inventory.poison_arrows:
            entry_name += " (חיצים מורעלים: %d)" % state.inventory.poison_arrows
        width = canvas.text(canvas.font_small, entry_name, (0, 0, 0)).get_width()
        _label(canvas, entry_name, (SCREEN_W // 2 - width // 2 - 6, HOTBAR_Y - 26), (230, 230, 230))

    hint = interact_hint(state)
    if hint:
        _draw_box(canvas, canvas.text(canvas.font, hint, (255, 226, 150)), HOTBAR_Y - 60,
                  border=(110, 100, 70))

    feedback = state.feedback
    if feedback.message_timer > 0:
        _draw_box(canvas, canvas.text(canvas.font, feedback.message, (255, 255, 255)), 42)
