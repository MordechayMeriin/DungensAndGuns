# -*- coding: utf-8 -*-
"""בונה שלב חדש: מבוך, יציאה, אויבים, משאבים, תיבות ומים."""

import random

from ..config import TILE
from ..data import CATALOG
from ..models import Crate, CrateKind, Enemy, Level, Resource, Tile
from .maze import Grid, generate_maze, path_exists

START_TILE = (1, 1)


def tile_center(tx: int, ty: int) -> tuple[float, float]:
    return tx * TILE + TILE / 2, ty * TILE + TILE / 2


def make_enemy(level: Level, x: float, y: float) -> Enemy:
    weapon = CATALOG.enemy_weapons[random.randrange(level.max_weapon)]
    hp = 30 + level.number * 6
    return Enemy(x=x, y=y, weapon=weapon, hp=hp, max_hp=hp)


def build_level(number: int) -> Level:
    cols = 15 + number * 2 | 1
    rows = 11 + number * 2 | 1
    grid = generate_maze(cols, rows)

    free = [(x, y) for y in range(rows) for x in range(cols)
            if grid[y][x] == Tile.FLOOR and not (x <= 2 and y <= 2)]
    random.shuffle(free)

    exit_tile = max(free, key=lambda t: t[0] + t[1])
    free.remove(exit_tile)

    def take(n: int) -> list[tuple[int, int]]:
        return [free.pop() for _ in range(min(n, len(free)))]

    level = Level(number=number, cols=cols, rows=rows, grid=grid, exit_tile=exit_tile,
                  max_weapon=min(6 + number * 2, len(CATALOG.enemy_weapons)))

    for tx, ty in take(min(3 + number, 12)):
        level.enemies.append(make_enemy(level, *tile_center(tx, ty)))

    kinds = [r.kind for r in CATALOG.resources]
    weights = [r.weight for r in CATALOG.resources]
    for tx, ty in take(9 + number * 2):
        x, y = tile_center(tx, ty)
        level.resources.append(Resource(x=x, y=y, kind=random.choices(kinds, weights=weights)[0]))

    for tx, ty in take(4 + number // 2):
        roll = random.random()
        kind = CrateKind.GOOD if roll < 0.6 else (CrateKind.BAD if roll < 0.8 else CrateKind.EMPTY)
        x, y = tile_center(tx, ty)
        level.crates.append(Crate(x=x, y=y, kind=kind))

    place_water(level.grid, free, exit_tile, target=5 + number * 2)
    return level


def place_water(grid: Grid, candidates: list[tuple[int, int]], exit_tile: tuple[int, int],
                target: int) -> None:
    """פורס שלוליות מים, אבל תמיד משאיר דרך יבשה מההתחלה ליציאה."""
    random.shuffle(candidates)
    placed = 0
    for x, y in candidates:
        if placed >= target:
            break
        grid[y][x] = Tile.WATER
        if path_exists(grid, START_TILE, exit_tile):
            placed += 1
        else:
            grid[y][x] = Tile.FLOOR
    water = [(x, y) for y, row in enumerate(grid) for x, tile in enumerate(row)
             if tile == Tile.WATER]
    random.shuffle(water)
    for x, y in water[:max(1, len(water) // 3)]:
        grid[y][x] = Tile.FISH
