import pygame
import random
from pygame import Vector2 as Vec2
from .timer import Timer
from .font import fonts
from .easing import lerp, ease_out_elastic
from . import easing
from .mgl import shader_handler

class ComboManager:

    def __init__(self):
        self.kills = 0
        self.kill_timer = Timer(30, done=True)
        self.hiding_timer = Timer(30)
        # self.kill_timer = Timer(300, done=True)
        # self.hiding_timer = Timer(300, done=True)
        self.showing = False

    def add_kills(self, kill_count):
        self.kills += kill_count
        self.kill_timer.reset()
        if not self.showing:
            self.showing = True

    def update(self):
        self.kill_timer.update()
        self.hiding_timer.update()

    def end_combo(self):
        if not self.showing: return
        self.kills = 0
        self.hiding_timer.reset()
        self.showing = False

    def render(self, surf, offset):
        img = fonts['big'].get_surf(f'{self.kills}X Combo!')
        x = ease_out_elastic(self.kill_timer.ratio)
        scale = (lerp(1/3, 1, x), lerp(3, 1, x))
        scale = (lerp(3, 1, x), lerp(1/3, 1, x))
        img = pygame.transform.scale(img, (img.get_width()*scale[0], img.get_height()*scale[1]))
        img = pygame.transform.rotate(img, lerp(random.randint(-20, 20), 0, x))

        hiding_timer_ratio = 1-self.hiding_timer.ratio
        if self.showing:
            surf.blit(img, (550, 50 ) - 0.5*Vec2(img.get_size()))
            shader_handler.vars['comboShowTimer'] = 1
        else:
            showing_timer_ratio = easing.ease_out_back(hiding_timer_ratio)
            surf.blit(img, (550 + (1-showing_timer_ratio)*150, 50 ) - 0.5*Vec2(img.get_size()))
            shader_handler.vars['comboShowTimer'] = hiding_timer_ratio
            print(self.hiding_timer)

        shader_handler.vars['killTimer'] = self.kill_timer.ratio

