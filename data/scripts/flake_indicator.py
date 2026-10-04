import pygame
import random
from .timer import Timer
from .font import fonts
from . import config
from .easing import lerp, ease_out_elastic
from .entity import PhysicsEntity

class Flake(PhysicsEntity):

    def __init__(self, game, *args, **kwargs):
        self.game = game
        super().__init__(*args, name='flake', action='idle', **kwargs)
        self.remove = False
        self.timer = Timer(60*6)
        self.t = 0

    def visual_update(self):
        self.t += 1

    def update(self, rects=None):
        self.vel[1] += 0.1
        if self.timer.done:
            self.remove = True
        self.visual_update()
        self.timer.update()
        super().update(rects)
        return {'remove': self.remove}

    @property
    def img(self):
        og_img = super().img
        return pygame.transform.rotate(og_img, self.t*2)

    def on_collision(self, entity):
        if entity.tag == 'player1':
            self.remove = True
            self.game.game_map.level.flake_indicator.add_flake()
        return super().on_collision(entity)

    def render(self, *args, offset=(0, 0), **kwargs):
        render = True
        if self.timer.ratio > 0.8:
            if (self.timer.frame % 6) >= 3:
                render = False
            
        if render:
            offset = pygame.Vector2(offset)
            offset -= 0.5*(pygame.Vector2(self.img.get_size()) - super().img.get_size())
            return super().render(*args, offset=offset, **kwargs)

class FlakeIndicator:

    def __init__(self):
        self.flakes = 0
        self.flake_change_timer = Timer(60, done=True)
        self.generate_surf()
        self.flake = Flake(None, pos=(self.w+10, 0))

    def generate_surf(self):
        text_surf = fonts['big'].get_surf(f'{self.flakes}')
        w = text_surf.get_width()
        surf = pygame.Surface((w + 20, text_surf.get_height()))
        surf.blit(text_surf)
        self.w = w
        self.surf = surf
        self.surf.set_colorkey((0, 0, 0))

    def add_flake(self, count=1):
        self.flakes += count
        self.flake_change_timer.reset()
        self.generate_surf()

    def update(self):
        self.flake_change_timer.update()
        self.flake.visual_update()

    def render(self, surf):
        img = self.surf.copy()
        self.flake.render(img)
        x = ease_out_elastic(self.flake_change_timer.ratio)
        scale = (lerp(1/3, 1, x), lerp(3, 1, x))
        scale = (lerp(3, 1, x), lerp(1/3, 1, x))
        img = pygame.transform.scale(img, (img.get_width()*scale[0], img.get_height()*scale[1]))
        img = pygame.transform.rotate(img, lerp(random.randint(-20, 20), 0, x))
        surf.blit(img, (config.GAME_SIZE[0]-98, 50) - 0.5*pygame.Vector2(img.get_size()))
