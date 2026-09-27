# -*- coding: utf-8 -*-
"""תמונות קטנות של פריטים: תצלום אמיתי מתיקיית images אם יש, ואחרת ציור."""

import os

import pygame

from ...config import IMAGE_DIR
from ...models import ItemBase
from . import item_art as it
from . import weapon_art as wp
from .painter import ICON_H, ICON_SCALE, ICON_W, IconPainter

# art -> פונקציה שמציירת אותו
PAINTERS = {
    "pistol": wp.paint_glock, "revolver": wp.paint_revolver, "shotgun": wp.paint_shotgun,
    "smg": wp.paint_mp5, "ar_m16": wp.paint_m16, "ar_ak": wp.paint_ak47,
    "sniper": wp.paint_awp, "sniper_big": wp.paint_barrett,
    "mg": wp.paint_m249, "mg_heavy": wp.paint_m2, "minigun": wp.paint_minigun,
    "dagger": wp.paint_dagger, "sword": wp.paint_sword, "spear": wp.paint_spear,
    "bow": wp.paint_bow, "sling": wp.paint_sling, "shuriken": wp.paint_shuriken,
    "grenade": wp.paint_grenade, "smoke": wp.paint_smoke,
    "shield": it.paint_shield, "vest": it.paint_vest, "helmet": it.paint_helmet,
    "sight": it.paint_sight, "laser": it.paint_laser, "launcher": it.paint_launcher,
    "wheel": it.paint_wheel,
    "ammo_pistol": it.paint_ammo_pistol, "ammo_rifle": it.paint_ammo_rifle,
    "ammo_revolver": it.paint_ammo_revolver, "ammo_smg": it.paint_ammo_smg,
    "ammo_ak": it.paint_ammo_ak, "ammo_arrow": it.paint_ammo_arrow,
    "ammo_shell": it.paint_ammo_shell, "ammo_sniper": it.paint_ammo_sniper,
    "ammo_mg": it.paint_ammo_mg,
    "saw": it.paint_saw, "pickaxe": it.paint_pickaxe, "sickle": it.paint_sickle,
    "rod": it.paint_rod, "torch": it.paint_torch, "boat": it.paint_boat,
    "potion_small": lambda g: it.paint_potion(g, 0),
    "potion_medium": lambda g: it.paint_potion(g, 1),
    "potion_large": lambda g: it.paint_potion(g, 2),
}

# פריטים שיש להם תצלום אמיתי בשם קובץ אחר
PHOTO_ALIAS = {
    "glock19": "glock", "sig": "p226", "browning": "m2",
    "barrett82": "barrett", "barrett_mg": "barrett",
    # דגמים שנראים כמעט זהים לדגם שיש לו תצלום
    "glock47": "glock17", "m16a3": "m16a2", "akms": "akm",
    "m4a2": "m4a1", "m4a3": "m4a1", "m4a4": "m4a1",
}


def load_photo(item_id: str) -> pygame.Surface | None:
    path = os.path.join(IMAGE_DIR, "%s.png" % PHOTO_ALIAS.get(item_id, item_id))
    if not os.path.exists(path):
        return None
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error:
        return None


def fit_image(image: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    """מקטין תמונה כך שתיכנס לתיבה בלי להימתח, וממרכז אותה."""
    out = pygame.Surface(size, pygame.SRCALPHA)
    k = min(size[0] / image.get_width(), size[1] / image.get_height())
    scaled = pygame.transform.smoothscale(
        image, (max(1, int(image.get_width() * k)), max(1, int(image.get_height() * k))))
    out.blit(scaled, ((size[0] - scaled.get_width()) // 2, (size[1] - scaled.get_height()) // 2))
    return out


def paint_icon(art: str, size: tuple[int, int]) -> pygame.Surface:
    work = pygame.Surface((ICON_W * ICON_SCALE, ICON_H * ICON_SCALE), pygame.SRCALPHA)
    PAINTERS.get(art, wp.paint_glock)(IconPainter(work, ICON_SCALE))
    return pygame.transform.smoothscale(work, size)


class IconCache:
    """בונה כל תמונה פעם אחת בלבד ושומר אותה."""

    def __init__(self):
        self._photos: dict[str, pygame.Surface | None] = {}
        self._icons: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}

    def get(self, item: ItemBase, size: tuple[int, int]) -> pygame.Surface:
        key = (item.id, size)
        if key not in self._icons:
            if item.id not in self._photos:
                self._photos[item.id] = load_photo(item.id)
            photo = self._photos[item.id]
            self._icons[key] = fit_image(photo, size) if photo else paint_icon(item.art, size)
        return self._icons[key]
