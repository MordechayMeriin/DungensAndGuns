# -*- coding: utf-8 -*-
"""איזה מקש עושה מה."""

import pygame

from .models import PlayerInput

MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT = pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
SHOOT = pygame.K_SPACE
INTERACT = pygame.K_q
DRINK = pygame.K_t
SHOP = pygame.K_y
SOUND = pygame.K_m
RESTART = pygame.K_r
NEXT_WEAPON = pygame.K_x
PREV_WEAPON = pygame.K_z
MENU = pygame.K_ESCAPE                   # תפריט ראשי
CONFIRM = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)   # בחירה בתפריט


def read_player_input(keys) -> PlayerInput:
    """מקשים שמחזיקים לחוצים (תזוזה, ירי...) -> מה השחקן רוצה לעשות בפריים הזה."""
    return PlayerInput(
        dx=float(keys[MOVE_RIGHT]) - float(keys[MOVE_LEFT]),
        dy=float(keys[MOVE_DOWN]) - float(keys[MOVE_UP]),
        shoot=bool(keys[SHOOT]),
        interact=bool(keys[INTERACT]),
        drink=bool(keys[DRINK]),
    )


def weapon_slot(key: int) -> int | None:
    """מקשים 1-9 בוחרים נשק לפי המקום שלו ברשימה."""
    if pygame.K_1 <= key <= pygame.K_9:
        return key - pygame.K_1
    return None
