# -*- coding: utf-8 -*-
"""הפס העליון (חיים, כסף, נשק...), שורת העזרה וההודעות."""

import pygame

from ..config import SCREEN_H, SCREEN_W
from ..data import CATALOG
from ..models import GameState
from ..systems.interaction import interact_hint
from ..systems.inventory import current_weapon
from . import colors
from .canvas import Canvas

HELP_TEXT = ("חצים = תזוזה | רווח = ירי | Q = איסוף | T = תרופה | Y = חנות | "
             "Z/X = נשק | M = קול | קליק על אויב = הנשק שלו | Esc = תפריט")


def status_parts(state: GameState) -> list[tuple[str, tuple[int, int, int]]]:
    """מה כתוב בפס העליון, מימין לשמאל."""
    player, inv = state.player, state.inventory
    weapon = current_weapon(state)
    ratio = player.hp_ratio
    parts = [
        ("חיים: %d/%d" % (round(player.hp), player.max_hp), colors.hp_color(ratio)),
        ("כסף: %d" % inv.money, colors.TEXT),
        ("נשק: %s (%d/%d)" % (weapon.name, inv.weapon_index + 1, len(inv.weapons)), colors.TEXT),
        ("שלב: %d" % state.level.number, colors.TEXT),
        ("תרופות: %d" % sum(inv.potions.values()), colors.TEXT),
        ("רימונים: %d" % sum(inv.throwable_count(w.id) for w in CATALOG.throwables), colors.TEXT),
    ]
    ammo = CATALOG.ammo_for(weapon)
    if ammo:
        left = inv.ammo_count(ammo.id)
        color = colors.TEXT if left > 10 else (colors.HP_ORANGE if left else colors.HP_RED)
        parts.insert(3, ("%s: %d" % (ammo.unit, left), color))
    if player.sick:
        parts.insert(1, ("חולה!", (120, 220, 120)))
    if ratio <= 0.25:
        parts.insert(1, ("דיוק -20%", colors.HP_RED))
    return parts


def draw_hud(canvas: Canvas, state: GameState) -> None:
    screen = canvas.screen
    pygame.draw.rect(screen, (18, 18, 22), pygame.Rect(0, 0, SCREEN_W, 34))
    x = SCREEN_W - 14
    for label, color in status_parts(state):
        text = canvas.text(canvas.font, label, color)
        x -= text.get_width()
        screen.blit(text, (x, 7))
        x -= 26

    hint = interact_hint(state)
    if hint:
        text = canvas.text(canvas.font, hint, (255, 226, 150))
        box = pygame.Rect(SCREEN_W // 2 - text.get_width() // 2 - 12, SCREEN_H - 62,
                          text.get_width() + 24, 30)
        pygame.draw.rect(screen, (44, 44, 52), box, border_radius=6)
        pygame.draw.rect(screen, (110, 100, 70), box, 1, border_radius=6)
        screen.blit(text, (box.x + 12, box.y + 5))

    canvas.blit_centered_x(canvas.text(canvas.font_small, HELP_TEXT, (150, 150, 150)), SCREEN_H - 22)

    feedback = state.feedback
    if feedback.message_timer > 0:
        text = canvas.text(canvas.font, feedback.message, (255, 255, 255))
        box = pygame.Rect(SCREEN_W // 2 - text.get_width() // 2 - 12, 42, text.get_width() + 24, 30)
        pygame.draw.rect(screen, (45, 45, 52), box, border_radius=6)
        screen.blit(text, (box.x + 12, box.y + 5))
