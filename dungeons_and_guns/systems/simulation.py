# -*- coding: utf-8 -*-
"""פריים אחד של המשחק: מזיזים את השחקן ומעדכנים את כל העולם."""

import math

from ..models import GameState, ItemKind, PlayerInput
from . import combat, enemies, health, interaction, missions, particles, weather
from . import wheel as wheel_system
from .inventory import move_speed

INSPECT_MS = 5000


def is_paused(state: GameState, window_open: bool) -> bool:
    return state.game_over or window_open or state.wheel is not None


def step(state: GameState, inp: PlayerInput, window_open: bool = False) -> None:
    """מתקדם פריים אחד. בזמן חנות/תיק/גלגל/מוות העולם קפוא."""
    if state.wheel is not None:
        wheel_system.update(state)
    if is_paused(state, window_open):
        return
    update_player(state, inp)
    enemies.update_enemies(state)
    combat.update_bullets(state)
    combat.update_poison(state)
    health.update_sickness(state)
    combat.update_grenades(state)
    combat.update_smokes(state)
    particles.update_sparks(state.level)
    missions.update(state)
    weather.update(state)


def update_player(state: GameState, inp: PlayerInput) -> None:
    player = state.player
    if player.invuln > 0:
        player.invuln -= 1
    dx, dy = inp.dx, inp.dy
    if dx or dy:
        length = math.hypot(dx, dy)
        dx, dy = dx / length, dy / length
        player.dir = (dx, dy)
        speed = move_speed(state.inventory)
        boat = "boat" in state.inventory.tools
        if state.level.can_move(player.x + dx * speed, player.y, player.r, boat):
            player.x += dx * speed
        if state.level.can_move(player.x, player.y + dy * speed, player.r, boat):
            player.y += dy * speed

    if inp.shoot:
        use_selected(state)
    if inp.interact:
        interaction.interact(state)
    if inp.drink:
        health.drink_potion(state)
    if inp.eat:
        health.eat(state)


def use_selected(state: GameState) -> None:
    """רווח - משתמשים במה שנבחר בשורת המספרים: יורים, שותים או אוכלים."""
    item = state.inventory.selected_item
    if item is None:
        return
    match item.kind:
        case ItemKind.WEAPON:
            combat.player_shoot(state)
        case ItemKind.POTION:
            health.drink_potion(state, item.id)
        case ItemKind.FOOD:
            health.eat(state, item.id)


def inspect_enemy_at(state: GameState, wx: float, wy: float) -> None:
    """לחיצה על אויב (בקואורדינטות של העולם) - מראה איזה נשק יש לו."""
    for e in state.level.enemies:
        if math.hypot(wx - e.x, wy - e.y) <= e.r + 8:
            state.inspect_uid = e.uid
            state.inspect_until = state.now + INSPECT_MS
            return
    state.inspect_uid = None
