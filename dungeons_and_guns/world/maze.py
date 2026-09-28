# -*- coding: utf-8 -*-
"""יצירת מבוך אקראי ובדיקה שיש דרך מנקודה לנקודה."""

import random

from ..models import Tile

Grid = list[list[Tile]]


def generate_maze(w: int, h: int) -> Grid:
    """מבוך "חופר" (DFS): מתחיל מ-(1,1) ופותח מסדרונות עד שאין לאן להמשיך."""
    grid = [[Tile.WALL] * w for _ in range(h)]
    stack = [(1, 1)]
    grid[1][1] = Tile.FLOOR
    while stack:
        cx, cy = stack[-1]
        options = []
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            nx, ny = cx + dx, cy + dy
            if 0 < nx < w - 1 and 0 < ny < h - 1 and grid[ny][nx] == Tile.WALL:
                options.append((nx, ny, dx, dy))
        if options:
            nx, ny, dx, dy = random.choice(options)
            grid[cy + dy // 2][cx + dx // 2] = Tile.FLOOR
            grid[ny][nx] = Tile.FLOOR
            stack.append((nx, ny))
        else:
            stack.pop()
    return grid


def reachable(grid: Grid, start: tuple[int, int]) -> set[tuple[int, int]]:
    """כל המשבצות שאפשר להגיע אליהן ברגל (רק על רצפה) מ-start."""
    rows, cols = len(grid), len(grid[0])
    seen = {start}
    queue = [start]
    while queue:
        x, y = queue.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (0 <= nx < cols and 0 <= ny < rows
                    and (nx, ny) not in seen and grid[ny][nx] == Tile.FLOOR):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def path_exists(grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> bool:
    """האם אפשר ללכת ברגל (רק על רצפה) מ-start ל-goal."""
    return goal in reachable(grid, start)
