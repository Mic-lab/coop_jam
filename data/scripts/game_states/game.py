import pygame
from .state import State
# from .menu import Menu
from ..button import Button
from ..font import fonts
from ..game_map import GameMap
from .. import colors
from ..timer import Timer
from copy import deepcopy

class Game(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rects = [pygame.Rect(30, 30+i*30, 80, 20) for i in range(4)]
        self.buttons = {
        }

        self.game_map = GameMap(self)
        self.freeze_timer = Timer(0, done=True)
        self.just_unfroze = False
        self.saved_pressed_inputs = {}
        self.pending_freeze = 0

    def freeze(self, duration=5):
        self.freeze_timer = Timer(duration)

    def end_freeze(self, duration=5):
        if self.pending_freeze and duration < self.pending_freeze:
            return
        self.pending_freeze = duration

    def sub_update(self):

        # to ensure I still accept pressed inputs when game is frozen
        if self.just_unfroze:
            self.inputs['pressed'] |= self.saved_pressed_inputs
            self.saved_pressed_inputs = {}

        elif not self.freeze_timer.done:
            for key, val in filter(lambda x: x[1], self.inputs['pressed'].items()):
                self.saved_pressed_inputs[key] = True

        self.just_unfroze = False
        if self.freeze_timer.done: self.game_map.update()


        self.game_surf.fill((5, 6, 8))
        # self.game_surf.fill(colors.GRAY_3)
        self.game_surf.fill(colors.PURPLE_1)

        # Update Buttons
        for key, btn in self.buttons.items():
            if self.freeze_timer.done:
                btn.update(self.inputs)
            btn.render(self.game_surf)

            if btn.clicked:
                if key == 'menu':
                    self.handler.transition_to(self.handler.states.Menu)

        self.game_map.render(self.game_surf)
        old_frozen = self.freeze_timer.done
        self.freeze_timer.update()
        if self.freeze_timer.done and not old_frozen:
            self.just_unfroze = True

        if self.pending_freeze:
            self.freeze(self.pending_freeze)
            self.pending_freeze = 0
