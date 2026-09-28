# -*- coding: utf-8 -*-
"""איזה מקש עושה מה."""

import pygame

from .models import PlayerInput

MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT = pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
SHOOT = pygame.K_SPACE
INTERACT = pygame.K_q
DRINK = pygame.K_t
EAT = pygame.K_f
SHOP = pygame.K_y
SOUND = pygame.K_m
RESTART = pygame.K_r
BAG = pygame.K_e                         # התיק
NEXT_SLOT = pygame.K_x                   # משבצת הבאה בשורת המספרים
PREV_SLOT = pygame.K_z
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
        eat=bool(keys[EAT]),
    )


def hotbar_slot(key: int) -> int | None:
    """מקשים 1-9 ו-0 בוחרים משבצת בשורת המספרים (0 = העשירית)."""
    if pygame.K_1 <= key <= pygame.K_9:
        return key - pygame.K_1
    if key == pygame.K_0:
        return 9
    return None
