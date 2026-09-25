import pygame
from pygame.math import clamp
from .timer import Timer
from .animation import Animation
from . import easing, config, sfx
from .font import fonts
from .entity import Entity

class Shop:

    def __init__(self, game):
        self.game = game
        self.hide_timer = Timer(30, done=True)
        self.showing = False

        h = Animation.img_db['button'].get_height()

        def get_rect(i):
            return (0, 50+i*(h+10), 150, h)

        self.buttons = {
                'button_1': Button(get_rect(0), 'Hello world', 'basic'),
                'button_2': Button(get_rect(1), 'Hello world', 'basic'),
                'button_3': Button(get_rect(2), 'Hello world', 'basic'),
                'button_4': Button(get_rect(3), 'Hello world', 'basic'),
                        }

        self.fish = Entity((0, 0), 'fish_shop', action='idle')
        self.fish.real_pos[1] = config.GAME_SIZE[1] - self.fish.rect.h

    def show(self):
        self.showing = True

    def hide(self):
        self.showing = False

    def update(self):
        if self.showing:
            if self.hide_timer.ratio > 0:
                self.hide_timer.frame -= 1
                self.hide_timer.done = False
        else:
            self.hide_timer.update()

        for key, button in self.buttons.items():
            button.update(self.game.inputs, click_sound='buy.wav')

        self.fish.update()

    def render(self, surf):
        if self.hide_timer.done: return

        bg_img = Animation.img_db['shop_bg']

        t1 = 1-self.hide_timer.ratio
        t2 = clamp(1-self.hide_timer.ratio*1.1, 0, 1)

        bg_x = easing.lerp(0, bg_img.get_width()-50, easing.ease_out_back(t1))
        bg_x = config.GAME_SIZE[0] - bg_x
        surf.blit(bg_img, (bg_x, 0))



        fish_x = easing.lerp(0, -self.fish.rect.w+16, easing.ease_out_back(t1))
        self.fish.real_pos[0] = config.GAME_SIZE[0] + fish_x
        # print(self.fish.rect.x)
        self.fish.render(surf)

        i = 0
        for key, button in self.buttons.items():
            btn_x = easing.lerp(config.GAME_SIZE[0], config.GAME_SIZE[0]-110-i*8, easing.ease_out_back(t2))
            button.rect.x = btn_x
            offset_x = easing.lerp(0, -40, easing.ease_out_back(1-button.unselect_timer.ratio))
            button.render(surf, offset=(offset_x, 0))
            i += 1

class Button:
    
    presets = {
        'basic': {
            'colors': {'border': [91, 77, 76], 
                       'fill': [151, 134, 125], 
                       'text': [240, 240, 240] }
        },
    }
    
    def __init__(self, rect: pygame.Rect, text, preset):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.preset = preset
        self.selected = False
        self.clicked = False
        self.released = False
        self.disabled = False
        self.generate_surf()
        self.unselect_timer = Timer(10, done=True)

    def disable(self):
        self.disabled = True
        self.generate_surf()

    def enable(self):
        self.disabled = False
        self.generate_surf()

    def generate_surf(self):
        # self.surf = pygame.Surface(self.rect.size)
        # self.surf.set_colorkey((0, 0, 0))
        # rect = pygame.Rect(0, 0, *self.rect.size)
        # pygame.draw.rect(self.surf, self.colors['border'], rect, border_radius=2)
        # x, y, w, h = rect
        # x += 1
        # y += 1
        # w -= 2
        # h -= 3
        # pygame.draw.rect(self.surf, self.colors['fill'], (x, y, w, h), border_radius=2)
        # # pygame.draw.aaline(self.surf, self.colors['text'], (x, y), (x, y + h - 2))
        # # pygame.draw.aaline(self.surf, self.colors['text'], (x, y), (x + w - 1, y))
        # self.surf.blit(text_img, (rect.centerx - text_img.get_width()*0.5,
        #                      rect.centery - text_img.get_height()*0.5 - 1))

        bg =  Animation.img_db['button']
        s = pygame.Surface(bg.get_size())
        s.blit(bg)
        s.set_colorkey((0,0,0))

        text_img = fonts[self.presets[self.preset].get('font', 'shop')].get_surf(self.text, color=self.colors['text'])
        s.blit(text_img, (16, 0.5*(s.get_height()-text_img.get_height())))
        self.surf = s
        
    def update(self, inputs, select_sound='select.wav', click_sound='click.wav'):
        if self.disabled: return

        self.clicked = False
        if self.rect.collidepoint(inputs.get('game_mouse_pos')):
            if not self.selected:
                sfx.sounds[select_sound].play()
            self.selected = True
            if inputs['pressed'].get('mouse1'):
                self.clicked = True
                sfx.sounds[click_sound].play()
        else:
            self.selected = False



        if self.selected:
            if self.unselect_timer.frame:
                self.unselect_timer.frame -= 1
                self.unselect_timer.done = False
        else:
            self.unselect_timer.update()

        # self.generate_surf()
                
    def render(self, surf, offset):
        surf.blit(self.surf, self.rect.topleft + pygame.Vector2(offset))

    @property
    def colors(self):
        # if self.disabled:
        #     colors = self.presets[self.preset]['colors'].copy()
        #     colors['fill'] = colors['border']
        #     return colors
        return self.presets[self.preset]['colors']

        if not self.selected:
            return self.presets[self.preset]['colors']
        else:
            if self.clicked:
                change = 2
            else:
                change = 1

            return modes

