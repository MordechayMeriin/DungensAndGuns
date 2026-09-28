# -*- coding: utf-8 -*-
"""ריבוע של פריט - בשורת המספרים ובתיק: תמונה, כמה יש, ומספר המקש."""

from typing import NamedTuple

import pygame

from ..config import SCREEN_W
from ..data import CATALOG
from ..models import HOTBAR_SIZE, GameState, ItemBase, ItemKind, SlotItem
from .canvas import Canvas

SLOT = 50           # גודל ריבוע
GAP = 6             # רווח בין ריבועים
SELECTED = (255, 214, 102)


class Entry(NamedTuple):
    """מה מציירים בריבוע אחד."""

    name: str
    count: str = ""                     # המספר הקטן בפינה ("" = בלי מספר)
    item: ItemBase | None = None        # התמונה - לפי פריט מהקטלוג...
    art: str = ""                       # ...או לפי שם של ציור (חומרים)
    slot_item: SlotItem | None = None   # מה נכנס לשורת המספרים כשגוררים (None = אי אפשר)


def slot_entry(state: GameState, item: SlotItem) -> Entry:
    """ריבוע של דבר שאפשר לשים בשורה. בנשק - כמה כדורים נשארו."""
    inv = state.inventory
    match item.kind:
        case ItemKind.WEAPON:
            w = CATALOG.weapon(item.id)
            if w.is_throwable:
                count = str(inv.throwable_count(w.id))
            else:
                ammo = CATALOG.ammo_for(w)
                count = str(inv.ammo_count(ammo.id)) if ammo else ""
            return Entry(w.name, count, w, slot_item=item)
        case ItemKind.POTION:
            p = CATALOG.potion(item.id)
            return Entry(p.name, str(inv.potion_count(p.id)), p, slot_item=item)
        case _:
            f = CATALOG.food(item.id)
            return Entry(f.name, str(inv.food_count(f.id)), f, slot_item=item)


def hotbar_entries(state: GameState) -> list[Entry | None]:
    return [slot_entry(state, item) if item else None for item in state.inventory.hotbar]


def hotbar_rects(y: int, cx: int = SCREEN_W // 2) -> list[pygame.Rect]:
    """עשרת הריבועים של השורה, משמאל לימין כמו המספרים במקלדת (1 עד 0)."""
    width = HOTBAR_SIZE * SLOT + (HOTBAR_SIZE - 1) * GAP
    left = cx - width // 2
    return [pygame.Rect(left + i * (SLOT + GAP), y, SLOT, SLOT) for i in range(HOTBAR_SIZE)]


def key_label(index: int) -> str:
    return str((index + 1) % 10)


def draw_slot(canvas: Canvas, rect: pygame.Rect, entry: Entry | None, selected: bool = False,
              label: str = "", hover: bool = False) -> None:
    screen = canvas.screen
    pygame.draw.rect(screen, (62, 62, 72) if hover else (44, 44, 52), rect, border_radius=6)
    if entry is not None:
        icon = canvas.icons.square(entry.item, rect.w - 10, entry.art)
        screen.blit(icon, (rect.x + 5, rect.y + 5))
        if entry.count:
            color = (255, 110, 110) if entry.count == "0" else (255, 255, 255)
            text = canvas.text(canvas.font_small, entry.count, color)
            x, y = rect.right - 4 - text.get_width(), rect.bottom - 1 - text.get_height()
            screen.blit(canvas.text(canvas.font_small, entry.count, (0, 0, 0)), (x + 1, y + 1))
            screen.blit(text, (x, y))
    if label:
        screen.blit(canvas.text(canvas.font_small, label, (160, 160, 170)), (rect.x + 4, rect.y + 1))
    if selected:
        pygame.draw.rect(screen, SELECTED, rect.inflate(4, 4), 3, border_radius=7)
    else:
        pygame.draw.rect(screen, (92, 92, 106), rect, 1, border_radius=6)


def draw_hotbar(canvas: Canvas, state: GameState, rects: list[pygame.Rect],
                hover: int | None = None, hidden: int | None = None) -> None:
    """hidden = משבצת שגוררים ממנה עכשיו (מציירים אותה ריקה)."""
    for i, (rect, entry) in enumerate(zip(rects, hotbar_entries(state))):
        draw_slot(canvas, rect, None if i == hidden else entry,
                  selected=i == state.inventory.selected, label=key_label(i), hover=i == hover)


def slot_at(rects: list[pygame.Rect], pos: tuple[int, int]) -> int | None:
    return next((i for i, r in enumerate(rects) if r.collidepoint(pos)), None)


def draw_tooltip(canvas: Canvas, text: str, pos: tuple[int, int]) -> None:
    surf = canvas.text(canvas.font_small, text, (255, 255, 255))
    box = pygame.Rect(0, 0, surf.get_width() + 14, surf.get_height() + 8)
    box.bottomleft = (pos[0] + 12, pos[1] - 6)
    box.clamp_ip(canvas.screen.get_rect())
    pygame.draw.rect(canvas.screen, (20, 20, 24), box, border_radius=5)
    pygame.draw.rect(canvas.screen, (120, 120, 130), box, 1, border_radius=5)
    canvas.screen.blit(surf, (box.x + 7, box.y + 4))
