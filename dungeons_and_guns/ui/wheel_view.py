# -*- coding: utf-8 -*-
"""ציור גלגל המזל."""

import math

import pygame

from ..config import SCREEN_H, SCREEN_W
from ..data import CATALOG
from ..models import WheelSpin
from . import colors
from .canvas import Canvas


def draw_wheel(canvas: Canvas, w: WheelSpin) -> None:
    screen = canvas.screen
    canvas.dim(205)
    canvas.blit_centered_x(canvas.text(canvas.font_big, "גלגל המזל", colors.GOLD), 18)

    slices = CATALOG.wheel_slices
    cx, cy, radius = SCREEN_W // 2, SCREEN_H // 2 + 12, 158
    step = 2 * math.pi / len(slices)
    for i, slice_ in enumerate(slices):
        start = w.angle + i * step
        points = [(cx, cy)]
        for k in range(13):
            a = start + step * k / 12.0
            points.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))
        bright = w.done and w.result is not None and w.result.id == slice_.id
        color = slice_.color if not bright else tuple(min(255, c + 60) for c in slice_.color)
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (24, 24, 28), points, 2)

        mid = start + step / 2
        label = canvas.text(canvas.font_small, slice_.name,
                            (20, 20, 24) if sum(slice_.color) > 400 else (250, 250, 250))
        lx = cx + math.cos(mid) * radius * 0.63
        ly = cy + math.sin(mid) * radius * 0.63
        screen.blit(label, (lx - label.get_width() // 2, ly - label.get_height() // 2))

    pygame.draw.circle(screen, (40, 40, 46), (cx, cy), 22)
    pygame.draw.circle(screen, colors.GOLD, (cx, cy), 22, 3)
    pygame.draw.polygon(screen, colors.GOLD,
                        [(cx, cy - radius + 16), (cx - 14, cy - radius - 14),
                         (cx + 14, cy - radius - 14)])

    if w.done:
        text = canvas.text(canvas.font, w.text, (255, 255, 255))
        box = pygame.Rect(SCREEN_W // 2 - text.get_width() // 2 - 16, SCREEN_H - 78,
                          text.get_width() + 32, 34)
        pygame.draw.rect(screen, (44, 44, 52), box, border_radius=8)
        pygame.draw.rect(screen, colors.GOLD, box, 2, border_radius=8)
        screen.blit(text, (box.x + 16, box.y + 6))
        canvas.blit_centered_x(canvas.text(canvas.font_small, "לחץ על מקש כלשהו כדי להמשיך",
                                           (190, 190, 190)), SCREEN_H - 38)
