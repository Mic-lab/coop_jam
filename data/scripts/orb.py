import pygame
from .entity import Entity
from .config import GAME_SIZE
from .sfx import sounds
from . import colors

class HpBar(Entity):
    def __init__(self, pos, max_val, val=None):
        super().__init__(pos, name='hp_fg', action='idle')

        self.max_val = max_val
        if val is None: val = max_val
        self.val = val

    @property
    def ratio(self):
        return self.val/self.max_val

    def change_val(self, val_change):
        self.val += val_change

    def render(self, surf, offset=(0,0)):
        rect = self.rect
        rect.w *= self.ratio
        pygame.draw.rect(surf, colors.BLACK, self.rect)
        pygame.draw.rect(surf, colors.RED, rect)
        return super().render(surf, offset=pygame.Vector2(offset))

class Orb(Entity):

    def __init__(self, game, pos):
        super().__init__(pos, 'orb', action='idle', collision_mode='soft_tracked')
        self.game = game
        self.tag = 'orb'

    # def update(self):
    #     self.hp_bar.update()
    #     return super().update()

    def on_collision(self, entity):
        if entity.tag != 'enemy': return
        sounds['hit.wav'].play()
        self.game.game_map.level.hp_bar.change_val(-1)

    # def render(self, surf, offset):
    #     # self.hp_bar.render(surf, offset)
    #     return super().render(surf, offset)
