import pygame
import random
from pygame import Vector2 as Vec2
from .timer import Timer
from .font import fonts
from .easing import lerp, ease_out_elastic
from . import easing, sfx, colors
from .mgl import shader_handler
from .flake_indicator import Flake

class ComboManager:

    def __init__(self, level):
        self.level = level
        self.kills = 0
        self.old_kills = 0
        self.kill_timer = Timer(30, done=True)
        self.hiding_timer = Timer(30, done=True)
        # self.kill_timer = Timer(300, done=True)
        # self.hiding_timer = Timer(300, done=True)
        self.showing = False
        self.flake = Flake(None, pos=(0, 0))
        self.gained_flakes = 0

    def add_kills(self, kill_count):
        self.kills += kill_count

        if self.kills > 1:
            k = min(self.kills-1, 5)
            sfx.sounds[f'combo_{k}.wav'].play()
            self.gained_flakes += k
            self.flake_surf = fonts['basic'].get_surf(f'(+{self.gained_flakes}           )')

        self.kill_timer.reset()
        if not self.showing:
            self.showing = True

    def update(self):
        self.kill_timer.update()
        self.hiding_timer.update()
        self.flake.visual_update()

    def end_combo(self):
        if not self.showing: return
        if self.kills > 1:
            self.end_game_combo()
            self.hiding_timer.reset()

        self.old_kills = self.kills
        self.kills = 0
        self.showing = False

    def end_game_combo(self):
        sfx.sounds['combo_end.wav'].set_volume((self.kills-1)/4)
        sfx.sounds['combo_end.wav'].play()
        self.level.flake_indicator.add_flake(self.gained_flakes)
        self.gained_flakes = 0

        if self.kills >= 5 or 1:
            hp_gain = self.kills-4
            hp_gain = abs(hp_gain)
            self.level.hp_bar.change_val(hp_gain)
            surf = fonts['big'].get_surf(f'+{hp_gain} HP Bonus', color=colors.WHITE)
            surf.set_alpha(254)
            self.level.moving_surfs.append({
                'surf': surf,
                'vel': (0, -1),
                'alpha_change': 5,
                'pos': pygame.Vector2(self.level.player_2.rect.center),
                })

    def render(self, surf, offset):
        kills = self.kills if self.showing else self.old_kills
        img = fonts['big'].get_surf(f'{kills}X Combo!')

        x = ease_out_elastic(self.kill_timer.ratio)
        scale = (lerp(1/3, 1, x), lerp(3, 1, x))
        scale = (lerp(3, 1, x), lerp(1/3, 1, x))
        def transform(img, x):
            img = pygame.transform.scale(img, (img.get_width()*scale[0], img.get_height()*scale[1]))
            img = pygame.transform.rotate(img, lerp(random.randint(-20, 20), 0, x))
            return img

        img = transform(img, x)

        y = 75
        hiding_timer_ratio = 1-self.hiding_timer.ratio
        if self.showing and self.kills > 1:
            surf.blit(img, (550, y) - 0.5*Vec2(img.get_size()))
            shader_handler.vars['comboShowTimer'] = 1
            flake_surf = transform(self.flake_surf, x)
            pos = (550, y+20) - 0.5*Vec2(flake_surf.get_size())
            surf.blit(flake_surf, pos)
            self.flake.real_pos = pos + (25, 0)
            self.flake.render(surf)
        else:
            if not self.hiding_timer.done:
                showing_timer_ratio = easing.ease_out_back(hiding_timer_ratio)
                surf.blit(img, (550 + (1-showing_timer_ratio)*150, y ) - 0.5*Vec2(img.get_size()))
            shader_handler.vars['comboShowTimer'] = hiding_timer_ratio

        shader_handler.vars['killTimer'] = self.kill_timer.ratio

