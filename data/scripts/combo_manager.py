import pygame
import random
from pygame import Vector2 as Vec2
from .timer import Timer
from .font import fonts
from .easing import lerp, ease_out_elastic

class ComboManager:

    def __init__(self):
        self.kills = 0
        self.kill_timer = Timer(30, done=True)

    def add_kills(self, kill_count):
        self.kills += kill_count
        self.kill_timer.reset()

    def update(self):
        self.kill_timer.update()

    def end_combo(self):
        self.kills = 0

    def render(self, surf, offset):
        img = fonts['big'].get_surf(f'{self.kills}X Combo!')
        x = ease_out_elastic(self.kill_timer.ratio)
        scale = (lerp(1/3, 1, x), lerp(3, 1, x))
        scale = (lerp(3, 1, x), lerp(1/3, 1, x))
        img = pygame.transform.scale(img, (img.get_width()*scale[0], img.get_height()*scale[1]))
        img = pygame.transform.rotate(img, lerp(random.randint(-40, 40), 0, x))
        surf.blit(img, (400, 50) - 0.5*Vec2(img.get_size()))
