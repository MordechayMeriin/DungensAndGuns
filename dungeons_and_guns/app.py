# -*- coding: utf-8 -*-
"""החלון של המשחק והלולאה הראשית: קלט -> עדכון -> קולות -> ציור.

The app is a small state machine over four screens: the instructions (shown on every
launch), the main menu, the save/load slot picker, and the game itself. Esc from the game
opens the menu; the game clock only advances while the game screen is showing.
"""

from enum import StrEnum

import pygame

from . import controls
from .audio import SoundBank
from .config import FPS, SCREEN_H, SCREEN_W, TITLE
from .models import GameState
from .saves import SaveError, SaveStore, SlotInfo
from .systems import progression, shop, simulation
from .systems import wheel as wheel_system
from .ui.bag_view import BagView
from .ui.canvas import Canvas
from .ui.help_view import draw_help
from .ui.hud import draw_hud, game_hotbar_rects
from .ui.menu_view import MenuOption, MenuView
from .ui.overlays import draw_game_over, draw_inspect
from .ui.shop_view import SCROLL_KEYS, ShopView
from .ui.slots import slot_at
from .ui.wheel_view import draw_wheel
from .ui.world_view import WorldView

MAX_FRAME_MS = 100          # אם החלון נתקע (גרירה וכו') - לא מקפיצים את שעון המשחק


class Screen(StrEnum):
    HELP = "help"
    MENU = "menu"
    SLOTS = "slots"
    GAME = "game"


class SlotMode(StrEnum):
    SAVE = "save"
    LOAD = "load"


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.canvas = Canvas(pygame.display.set_mode((SCREEN_W, SCREEN_H)))
        self.clock = pygame.time.Clock()
        self.sfx = SoundBank()
        self.saves = SaveStore()
        self.world_view = WorldView(self.canvas)
        self.shop_view = ShopView(self.canvas)
        self.bag_view = BagView(self.canvas)
        self.menu = MenuView(self.canvas)
        self.state: GameState | None = None     # None = עוד לא התחיל משחק
        self.screen = Screen.MENU
        self.slot_mode = SlotMode.LOAD
        self.running = True
        self.screen = Screen.HELP           # כל הפעלה מתחילה בהוראות

    # ---------- מסכים ----------
    @property
    def can_save(self) -> bool:
        return self.state is not None and not self.state.game_over

    def open_menu(self, status: str = "") -> None:
        options = []
        if self.state is not None:
            options.append(MenuOption(id="resume", label="המשך משחק"))
        options.append(MenuOption(id="new", label="משחק חדש"))
        if self.can_save:
            options.append(MenuOption(id="save", label="שמירת משחק"))
        has_saves = self.saves.any_loadable()
        options.append(MenuOption(id="load", label="טעינת משחק", enabled=has_saves,
                                  detail="" if has_saves else "אין משחקים שמורים"))
        options.append(MenuOption(id="help", label="הוראות"))
        options.append(MenuOption(id="exit", label="יציאה"))
        self.menu.show(TITLE, options, subtitle="תפריט ראשי")
        self.menu.status = status
        self.screen = Screen.MENU

    def open_slots(self, mode: SlotMode) -> None:
        self.slot_mode = mode
        options = [self._slot_option(info, mode) for info in self.saves.slots()]
        options.append(MenuOption(id="back", label="חזרה"))
        title = "שמירת משחק" if mode == SlotMode.SAVE else "טעינת משחק"
        subtitle = "באיזו משבצת לשמור?" if mode == SlotMode.SAVE else "איזה משחק לטעון?"
        self.menu.show(title, options, subtitle)
        self.menu.status = ""
        self.screen = Screen.SLOTS

    @staticmethod
    def _slot_option(info: SlotInfo, mode: SlotMode) -> MenuOption:
        label = "משבצת %d" % info.slot
        if not info.exists:
            return MenuOption(id=str(info.slot), label=label, detail="ריקה",
                              enabled=mode == SlotMode.SAVE)
        if info.damaged:
            return MenuOption(id=str(info.slot), label=label, detail="קובץ פגום",
                              enabled=mode == SlotMode.SAVE)
        detail = "שלב %d | כסף %d | חיים %d | %s" % (
            info.level, info.money, info.hp, info.saved_at.strftime("%d/%m %H:%M"))
        if mode == SlotMode.SAVE:
            detail += " (יוחלף)"
        return MenuOption(id=str(info.slot), label=label, detail=detail)

    def resume(self) -> None:
        if self.state is not None:
            self.screen = Screen.GAME

    def start_game(self, state: GameState) -> None:
        self.state = state
        self.shop_view.open = False
        self.bag_view.open = False
        self.screen = Screen.GAME

    # ---------- פעולות תפריט ----------
    def choose(self, option: MenuOption) -> None:
        if self.screen == Screen.MENU:
            match option.id:
                case "resume":
                    self.resume()
                case "new":
                    self.start_game(progression.new_game())
                case "save":
                    self.open_slots(SlotMode.SAVE)
                case "load":
                    self.open_slots(SlotMode.LOAD)
                case "help":
                    self.screen = Screen.HELP
                case "exit":
                    self.running = False
        elif option.id == "back":
            self.open_menu()
        elif self.slot_mode == SlotMode.SAVE:
            self.save_to(int(option.id))
        else:
            self.load_from(int(option.id))

    def save_to(self, slot: int) -> None:
        try:
            self.saves.save(slot, self.state)
        except OSError:
            self.sfx.play("no")
            self.menu.status = "לא הצלחתי לשמור את הקובץ"
            return
        self.sfx.play("buy")
        self.resume()
        self.state.say("המשחק נשמר במשבצת %d" % slot)

    def load_from(self, slot: int) -> None:
        try:
            state = self.saves.load(slot)
        except SaveError:
            self.sfx.play("no")
            self.menu.status = "לא הצלחתי לטעון את המשחק - הקובץ פגום"
            return
        self.sfx.play("level")
        self.start_game(state)
        self.state.say("המשחק נטען - שלב %d" % state.level.number)

    # ---------- קלט ----------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif self.screen == Screen.HELP:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.open_menu()
        elif self.screen == Screen.GAME:
            self.handle_game_event(event)
        else:
            self.handle_menu_event(event)

    def handle_menu_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == controls.MENU:
                if self.screen == Screen.SLOTS:
                    self.open_menu()
                else:
                    self.resume()
            elif event.key in (controls.MOVE_UP, controls.MOVE_DOWN):
                self.menu.move(-1 if event.key == controls.MOVE_UP else 1)
            elif event.key in controls.CONFIRM and (option := self.menu.current()):
                self.choose(option)
        elif event.type == pygame.MOUSEMOTION:
            self.menu.hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if option := self.menu.option_at(event.pos):
                self.choose(option)

    def handle_game_event(self, event: pygame.event.Event) -> None:
        state = self.state
        if event.type == pygame.KEYDOWN:
            self.handle_game_key(event.key)
        elif event.type == pygame.MOUSEWHEEL:
            if self.shop_view.open:
                self.shop_view.scroll_by(-event.y * 120)
            elif self.bag_view.open:
                self.bag_view.scroll_by(-event.y * 60)
            elif state.wheel is None:
                state.inventory.cycle_slot(-event.y)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state.wheel is not None:
                wheel_system.close(state)
            elif self.shop_view.open:
                row = self.shop_view.row_at(event.pos)
                if row is not None:
                    shop.buy(state, row)
                    if state.wheel is not None:       # קנו סיבוב בגלגל - החנות נסגרת
                        self.shop_view.open = False
            elif self.bag_view.open:
                self.bag_view.press(state, event.pos)
            elif (slot := slot_at(game_hotbar_rects(), event.pos)) is not None:
                state.inventory.select_slot(slot)
            elif not state.game_over:
                simulation.inspect_enemy_at(state, *self.world_view.to_world(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.bag_view.open:
            self.drop(self.bag_view.release(event.pos))

    def drop(self, drop) -> None:
        """סוף גרירה בתיק: שמים במשבצת, מחליפים בין משבצות, או מוציאים מהשורה."""
        if drop is None:
            return
        inv = self.state.inventory
        if drop.to_slot is None:
            if drop.from_slot is not None:
                inv.clear_slot(drop.from_slot)
        elif drop.to_slot == drop.from_slot:
            inv.select_slot(drop.to_slot)             # סתם לחיצה על משבצת - בוחרים אותה
        else:
            inv.set_slot(drop.to_slot, drop.item)

    def handle_game_key(self, key: int) -> None:
        state, inv = self.state, self.state.inventory
        if key == controls.MENU:
            self.open_menu()
        elif state.wheel is not None:
            wheel_system.close(state)
        elif self.shop_view.open and key in SCROLL_KEYS:
            self.shop_view.scroll_by(SCROLL_KEYS[key])
        elif self.bag_view.open and key in SCROLL_KEYS:
            self.bag_view.scroll_by(SCROLL_KEYS[key])
        elif key == controls.SHOP and not state.game_over:
            self.bag_view.open = False
            self.shop_view.toggle()
        elif key == controls.BAG and not state.game_over:
            self.shop_view.open = False
            self.bag_view.toggle()
        elif key == controls.SOUND:
            state.say("הקולות דולקים" if self.sfx.toggle() else "הקולות כבויים")
        elif key == controls.RESTART and state.game_over:
            self.start_game(progression.new_game())
        elif key == controls.NEXT_SLOT:
            inv.cycle_slot(1)
        elif key == controls.PREV_SLOT:
            inv.cycle_slot(-1)
        elif (slot := controls.hotbar_slot(key)) is not None:
            inv.select_slot(slot)

    # ---------- ציור ----------
    def draw_game(self) -> None:
        state = self.state
        self.world_view.draw(state)
        draw_inspect(self.canvas, self.world_view, state)
        draw_hud(self.canvas, state)
        if state.wheel is not None:
            draw_wheel(self.canvas, state.wheel)
        elif self.shop_view.open:
            self.shop_view.draw(state)
        elif self.bag_view.open:
            self.bag_view.draw(state, pygame.mouse.get_pos())
        if state.game_over:
            draw_game_over(self.canvas, state)

    def draw(self) -> None:
        if self.screen == Screen.HELP:
            draw_help(self.canvas)
            pygame.display.flip()
            return
        if self.state is not None:
            self.draw_game()
        if self.screen != Screen.GAME:
            self.menu.draw(over_game=self.state is not None)
        pygame.display.flip()

    # ---------- לולאה ראשית ----------
    def update(self, elapsed_ms: int) -> None:
        if self.screen != Screen.GAME:
            return                          # בתפריט הזמן של המשחק עוצר
        state = self.state
        state.now += min(elapsed_ms, MAX_FRAME_MS)
        simulation.step(state, controls.read_player_input(pygame.key.get_pressed()),
                        window_open=self.shop_view.open or self.bag_view.open)
        for cue in state.feedback.drain_sounds():
            self.sfx.play(cue.name, gap=cue.gap)
        state.feedback.tick()

    def run(self) -> None:
        elapsed = 0
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            if not self.running:
                break
            self.update(elapsed)
            self.draw()
            elapsed = self.clock.tick(FPS)
        pygame.quit()


def main() -> None:
    App().run()
