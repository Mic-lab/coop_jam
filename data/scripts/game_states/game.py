import pygame
from .state import State
# from .menu import Menu
from ..button import Button
from ..font import fonts
from ..game_map import GameMap
from .. import colors
from ..timer import Timer

class Game(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rects = [pygame.Rect(30, 30+i*30, 80, 20) for i in range(4)]
        self.buttons = {
            'menu': Button(rects[0], 'back', 'basic'),
        }

        self.game_map = GameMap(self)
        self.freeze_timer = Timer(0, done=True)
        self.pending_freeze = 0

    def freeze(self, duration=5):
        self.freeze_timer = Timer(duration)

    def end_freeze(self, duration=5):
        if self.pending_freeze and duration < self.pending_freeze:
            return
        self.pending_freeze = duration

    def sub_update(self):

        if self.freeze_timer.done: self.game_map.update()


        self.game_surf.fill((5, 6, 8))
        self.game_surf.fill(colors.GRAY_3)

        # Update Buttons
        for key, btn in self.buttons.items():
            if self.freeze_timer.done:
                btn.update(self.inputs)
            btn.render(self.game_surf)

            if btn.clicked:
                if key == 'menu':
                    self.handler.transition_to(self.handler.states.Menu)

        self.game_map.render(self.game_surf)
        self.freeze_timer.update()

        if self.pending_freeze:
            self.freeze(self.pending_freeze)
            self.pending_freeze = 0
