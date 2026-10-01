# -*- coding: utf-8 -*-
"""ציור המבוך וכל מה שבתוכו."""

import math

import pygame

from ..config import SCREEN_H, SCREEN_W, TILE
from ..data import CATALOG
from ..models import GameState, Tile, WeaponKind
from ..systems import weather
from ..systems.inventory import current_weapon
from . import colors
from .canvas import Canvas


FOG_COLOR = (150, 156, 166)
FOG_ALPHA = 255


def make_fog_surface() -> pygame.Surface:
    """משטח ערפל גדול פי 2 מהמסך עם "חור" שקוף באמצע, שהולך ומתערפל לאט כלפי חוץ."""
    fog = pygame.Surface((SCREEN_W * 2, SCREEN_H * 2), pygame.SRCALPHA)
    fog.fill(FOG_COLOR + (FOG_ALPHA,))
    center = (SCREEN_W, SCREEN_H)
    inner, outer = weather.FOG_SIGHT - 40, weather.FOG_SIGHT + 30
    for r in range(outer, 0, -2):
        share = max(0.0, min(1.0, (r - inner) / (outer - inner)))
        pygame.draw.circle(fog, FOG_COLOR + (int(FOG_ALPHA * share),), center, r)
    return fog


def camera_for(state: GameState) -> tuple[float, float]:
    """המצלמה עוקבת אחרי השחקן; מבוך קטן מהמסך נשאר באמצע."""
    level, player = state.level, state.player
    if level.width <= SCREEN_W:
        cam_x = -(SCREEN_W - level.width) / 2
    else:
        cam_x = max(0, min(player.x - SCREEN_W / 2, level.width - SCREEN_W))
    if level.height <= SCREEN_H:
        cam_y = -(SCREEN_H - level.height) / 2
    else:
        cam_y = max(0, min(player.y - SCREEN_H / 2, level.height - SCREEN_H))
    return cam_x, cam_y


class WorldView:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.cam_x = 0.0
        self.cam_y = 0.0
        self._fog_surface: pygame.Surface | None = None

    def sx(self, x: float) -> int:
        return int(x - self.cam_x)

    def sy(self, y: float) -> int:
        return int(y - self.cam_y)

    def to_world(self, pos: tuple[int, int]) -> tuple[float, float]:
        return pos[0] + self.cam_x, pos[1] + self.cam_y

    def draw(self, state: GameState) -> None:
        self.cam_x, self.cam_y = camera_for(state)
        self.canvas.screen.fill((20, 20, 24))
        self._tiles(state)
        self._exit(state)
        self._resources(state)
        self._crates(state)
        self._enemies(state)
        self._player(state)
        self._projectiles(state)
        self._smoke(state)
        self._effects(state)
        self._fog(state)

    # ---------- חלקים ----------
    def _tiles(self, state: GameState) -> None:
        screen, level, sx, sy = self.canvas.screen, state.level, self.sx, self.sy
        x0, x1 = int(self.cam_x // TILE), int((self.cam_x + SCREEN_W) // TILE) + 1
        y0, y1 = int(self.cam_y // TILE), int((self.cam_y + SCREEN_H) // TILE) + 1
        for gy in range(max(0, y0), min(level.rows, y1)):
            for gx in range(max(0, x0), min(level.cols, x1)):
                rect = pygame.Rect(sx(gx * TILE), sy(gy * TILE), TILE, TILE)
                tile = level.grid[gy][gx]
                if tile == Tile.WALL:
                    pygame.draw.rect(screen, colors.WALL, rect)
                elif tile == Tile.ARMORED:
                    pygame.draw.rect(screen, colors.ARMORED, rect)
                    pygame.draw.rect(screen, colors.ARMORED_EDGE, rect.inflate(-4, -4), 2)
                    for cx, cy in ((7, 7), (TILE - 8, 7), (7, TILE - 8), (TILE - 8, TILE - 8)):
                        pygame.draw.circle(screen, colors.ARMORED_EDGE, (rect.x + cx, rect.y + cy), 2)
                elif tile == Tile.GATE:
                    pygame.draw.rect(screen, colors.FLOOR_A, rect)
                    pygame.draw.rect(screen, colors.GATE, rect.inflate(-2, -2), 3, border_radius=3)
                    for i in range(1, 4):
                        x = rect.x + i * TILE // 4
                        pygame.draw.line(screen, colors.GATE, (x, rect.y + 2), (x, rect.bottom - 3), 3)
                    pygame.draw.circle(screen, colors.EXIT, rect.center, 5)            # מנעול
                    pygame.draw.circle(screen, (60, 40, 10), rect.center, 2)
                elif tile.is_water:
                    pygame.draw.rect(screen, colors.WATER if (gx + gy) % 2 == 0 else colors.WATER_ALT, rect)
                    pygame.draw.line(screen, (70, 130, 200),
                                     (rect.x + 5, rect.y + 7), (rect.x + TILE - 6, rect.y + 7))
                    if tile == Tile.FISH:
                        ready = level.fish_cooldown.get((gx, gy), 0) <= state.now
                        fish_col = (240, 176, 72) if ready else (74, 110, 150)
                        pygame.draw.ellipse(screen, fish_col,
                                            pygame.Rect(rect.x + 10, rect.y + 16, 13, 8))
                        pygame.draw.polygon(screen, fish_col,
                                            [(rect.x + 10, rect.y + 20), (rect.x + 4, rect.y + 15),
                                             (rect.x + 4, rect.y + 25)])
                else:
                    pygame.draw.rect(screen, colors.FLOOR_A if (gx + gy) % 2 == 0 else colors.FLOOR_B, rect)

    def _exit(self, state: GameState) -> None:
        screen = self.canvas.screen
        ex, ey = state.level.exit_tile
        gate = pygame.Rect(self.sx(ex * TILE + 2), self.sy(ey * TILE + 2), TILE - 4, TILE - 4)
        pygame.draw.rect(screen, (62, 52, 20), gate, border_radius=4)          # פתח פתוח
        pygame.draw.rect(screen, colors.EXIT, gate, 3, border_radius=4)        # מסגרת
        bright = math.sin(state.now / 260.0) > 0
        arrow = (255, 236, 140) if bright else colors.EXIT
        acx, acy = gate.centerx, gate.centery
        pygame.draw.polygon(screen, arrow,
                            [(acx, acy - 9), (acx - 8, acy - 1), (acx - 3, acy - 1),
                             (acx - 3, acy + 8), (acx + 3, acy + 8), (acx + 3, acy - 1),
                             (acx + 8, acy - 1)])

    def _resources(self, state: GameState) -> None:
        screen, canvas = self.canvas.screen, self.canvas
        for res in state.level.resources:
            info = CATALOG.resource(res.kind)
            ready = res.ready_at <= state.now
            color = info.color if ready else tuple(c // 2 for c in info.color)
            cx, cy = self.sx(res.x), self.sy(res.y)
            pygame.draw.circle(screen, color, (cx, cy), 13)
            pygame.draw.circle(screen, (16, 16, 20), (cx, cy), 13, 1)
            text_col = (20, 20, 24) if sum(color) > 420 else (245, 245, 245)
            mark = canvas.text(canvas.font_small, info.mark, text_col)
            screen.blit(mark, (cx - mark.get_width() // 2, cy - mark.get_height() // 2))

    def _crates(self, state: GameState) -> None:
        screen, canvas = self.canvas.screen, self.canvas
        for crate in state.level.crates:
            rect = pygame.Rect(self.sx(crate.x) - 11, self.sy(crate.y) - 11, 22, 22)
            pygame.draw.rect(screen, colors.CRATE, rect, border_radius=3)
            pygame.draw.rect(screen, (90, 58, 26), rect, 2, border_radius=3)
            mark = canvas.font_small.render("?", True, (250, 226, 150))
            screen.blit(mark, (rect.centerx - mark.get_width() // 2,
                               rect.centery - mark.get_height() // 2))

    def _enemies(self, state: GameState) -> None:
        screen, player = self.canvas.screen, state.player
        for e in state.level.enemies:
            x, y = self.sx(e.x), self.sy(e.y)
            d = max(1.0, math.hypot(player.x - e.x, player.y - e.y))
            if "laser" in e.gear and weather.can_see(state, d):       # קו לייזר אדום אליך
                reach = min(d, e.weapon.rng)
                pygame.draw.line(screen, (255, 70, 70), (x, y),
                                 (self.sx(e.x + (player.x - e.x) / d * reach),
                                  self.sy(e.y + (player.y - e.y) / d * reach)), 1)
            pygame.draw.circle(screen, colors.ENEMY, (x, y), e.r)
            if "vest" in e.gear:
                pygame.draw.circle(screen, (84, 92, 60), (x, y), e.r - 3, 3)
            if "helmet" in e.gear:
                pygame.draw.ellipse(screen, (70, 80, 64), pygame.Rect(x - 8, y - e.r - 2, 16, 10))
            if "shield" in e.gear:                                    # מגן בצד שפונה אליך
                sx_, sy_ = x + int((player.x - e.x) / d * (e.r + 3)), y + int((player.y - e.y) / d * (e.r + 3))
                pygame.draw.circle(screen, (150, 160, 180), (sx_, sy_), 6)
                pygame.draw.circle(screen, (90, 96, 110), (sx_, sy_), 6, 1)
            if e.grenades.get("grenade") or e.grenades.get("smoke"):
                pygame.draw.circle(screen, (72, 92, 62), (x + e.r - 3, y + e.r - 3), 3)
            if e.poison_until > state.now:                     # מורעל - טבעת ירוקה
                pygame.draw.circle(self.canvas.screen, (120, 230, 90),
                                   (self.sx(e.x), self.sy(e.y)), e.r + 2, 2)
            self.canvas.bar(self.sx(e.x), self.sy(e.y) - e.r - 10, 26, e.hp / e.max_hp, (227, 51, 51))

    def _player(self, state: GameState) -> None:
        screen, player, sx, sy = self.canvas.screen, state.player, self.sx, self.sy
        color = (122, 184, 232) if player.invuln > 0 else colors.PLAYER
        pygame.draw.circle(screen, color, (sx(player.x), sy(player.y)), player.r)
        pygame.draw.circle(screen, (255, 255, 255),
                           (sx(player.x + player.dir[0] * 10), sy(player.y + player.dir[1] * 10)), 3)
        ratio = player.hp_ratio
        self.canvas.bar(sx(player.x), sy(player.y) - 24, 30, ratio, colors.hp_color(ratio))
        if player.sick:
            pygame.draw.circle(screen, (120, 210, 120), (sx(player.x), sy(player.y)), 15, 2)

    def _projectiles(self, state: GameState) -> None:
        screen, sx, sy = self.canvas.screen, self.sx, self.sy
        for b in state.level.bullets:
            pygame.draw.circle(screen, (255, 224, 102) if b.from_player else (255, 102, 102),
                               (sx(b.x), sy(b.y)), 3)
        for gr in state.level.grenades:
            if gr.weapon.kind == WeaponKind.PLACE:
                self._charge(state, gr)
                continue
            color = (120, 126, 132) if gr.weapon.id == "smoke" else (72, 92, 62)
            pygame.draw.circle(screen, color, (sx(gr.x), sy(gr.y)), 6)
            pygame.draw.circle(screen, (30, 30, 34), (sx(gr.x), sy(gr.y)), 6, 1)
            if (state.now // 120) % 2 == 0:
                pygame.draw.circle(screen, (255, 210, 90), (sx(gr.x), sy(gr.y) - 7), 2)

    def _charge(self, state: GameState, gr) -> None:
        """לבנת חבלה על הרצפה: TNT אדום או סמטקס בהיר, עם נורה שמהבהבת מהר יותר לקראת הבום."""
        screen, x, y = self.canvas.screen, self.sx(gr.x), self.sy(gr.y)
        body = pygame.Rect(x - 9, y - 6, 18, 12)
        if gr.weapon.id == "tnt":
            for i in range(3):
                pygame.draw.rect(screen, (196, 44, 40), pygame.Rect(body.x + i * 6, body.y, 5, 12), border_radius=2)
            pygame.draw.line(screen, (30, 30, 30), (body.x, body.centery), (body.right, body.centery), 2)
        else:
            pygame.draw.rect(screen, (222, 204, 160), body, border_radius=3)
            pygame.draw.rect(screen, (90, 90, 96), body, 1, border_radius=3)
        left = gr.fuse - state.now
        blink = 90 if left < 1000 else 220
        if (state.now // blink) % 2 == 0:
            pygame.draw.circle(screen, (255, 60, 60), (x, y - 9), 3)

    def _fog(self, state: GameState) -> None:
        """ערפל אפור על כל המסך, חוץ מעיגול קטן מסביב לשחקן."""
        strength = weather.fog_strength(state)
        if strength <= 0:
            return
        if self._fog_surface is None:
            self._fog_surface = make_fog_surface()
        fog = self._fog_surface
        fog.set_alpha(int(255 * strength))
        px, py = self.sx(state.player.x), self.sy(state.player.y)
        self.canvas.screen.blit(fog, (px - fog.get_width() // 2, py - fog.get_height() // 2))

    def _smoke(self, state: GameState) -> None:
        for cloud in state.level.smokes:
            left = cloud.until - state.now
            alpha = min(170, max(0, left // 6))
            radius = int(cloud.r)
            puff = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(puff, (198, 200, 206, alpha), (radius, radius), radius)
            pygame.draw.circle(puff, (214, 216, 222, alpha), (radius, radius), int(radius * 0.7))
            self.canvas.screen.blit(puff, (self.sx(cloud.x - radius), self.sy(cloud.y - radius)))

    def _effects(self, state: GameState) -> None:
        screen, player, sx, sy = self.canvas.screen, state.player, self.sx, self.sy
        if state.now < player.swing_until:
            reach = int(player.swing_reach)
            face = math.atan2(player.dir[1], player.dir[0])
            box = pygame.Rect(sx(player.x) - reach, sy(player.y) - reach, reach * 2, reach * 2)
            pygame.draw.arc(screen, (255, 248, 190), box, -face - 1.0, -face + 1.0, 3)

        weapon = current_weapon(state)
        if "laser" in state.inventory.gear and weapon is not None and not state.game_over:
            reach = min(weapon.rng, 260)
            pygame.draw.line(screen, (255, 80, 80), (sx(player.x), sy(player.y)),
                             (sx(player.x + player.dir[0] * reach), sy(player.y + player.dir[1] * reach)), 1)

        for s in state.level.sparks:
            pygame.draw.rect(screen, s.color, pygame.Rect(sx(s.x) - 2, sy(s.y) - 2, 4, 4))
