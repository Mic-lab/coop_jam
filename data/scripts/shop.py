import pygame
from pygame.math import clamp
from .timer import Timer
from .animation import Animation
from . import easing, config, sfx, colors
from .font import fonts
from .entity import Entity

class Shop:

    def __init__(self, game):
        self.game = game
        self.hide_timer = Timer(30, done=True)
        self.showing = False

        h = Animation.img_db['button'].get_height()

        def get_rect(i):
            return (0, 80+i*(h+10), 150, h)

        self.buttons = {
                'double_jump': Button(get_rect(0), 'P1: Double Jump', 'basic', 1, click_sound='buy.wav'),
                'high_jump': Button(get_rect(1), 'P1: High jump', 'basic', 2, click_sound='buy.wav'),
                'sprint': Button(get_rect(2), 'P1: Sprint', 'basic', 30, click_sound='buy.wav'),
                'big_bubble': Button(get_rect(3), 'P2: Big Bubble', 'basic', 30, click_sound='buy.wav'),
                'kill_reset': Button(get_rect(4), 'P2: Bubble Kill Reset', 'basic', 40, click_sound='buy.wav'),
                'done': Button(get_rect(5), 'Done', 'basic', 4, bg=Animation.img_db['button_done'], click_sound='shop_exit.wav')
                        }
        self.last_mouse_pos = None

        self.fish = Entity((0, 0), 'fish_shop', action='idle')
        self.fish.real_pos[1] = config.GAME_SIZE[1] - self.fish.rect.h
        self.description_surf = None

    def show(self):
        self.showing = True

        k = next(iter(self.buttons.keys()))
        self.selected_button = (0, k)
        self.buttons[k].select(select_sound=None)
        self.last_mouse_pos = None
        print(k)


    def hide(self):
        self.showing = False
        self.buttons[self.selected_button[1]].selected = False

    def update(self):
        if self.showing:
            if self.hide_timer.ratio > 0:
                self.hide_timer.frame -= 1
                self.hide_timer.done = False
        else:
            self.hide_timer.update()


        self.fish.update()

        if self.showing:
            self.update_buttons()

    def generate_description_surf(self):
        self.description_surf = fonts['shop'].get_surf(self.buttons[self.selected_button[1]].description)

    def update_buttons(self):
        ignore_mouse = True
        if self.game.inputs['game_mouse_pos'] != self.last_mouse_pos or self.game.inputs['pressed'].get('mouse1'):
            self.last_mouse_pos = self.game.inputs['game_mouse_pos']
            ignore_mouse = False

        new_selected_button = None
        i = 0
        for key, button in self.buttons.items():
            button.update(self.game.inputs, ignore_mouse=ignore_mouse)
            if button.selected and key != self.selected_button[1]:
                new_selected_button = i, key
                self.generate_description_surf()
            i += 1

        if ignore_mouse:
            new_index = None
            if self.game.inputs['pressed'].get('up') or self.game.inputs['pressed'].get('w'):
                new_index = self.selected_button[0]-1
            elif self.game.inputs['pressed'].get('down') or self.game.inputs['pressed'].get('s'):
                new_index = self.selected_button[0]+1
                print('going down')

            if new_index is not None and (0 <= new_index < len(self.buttons)):
                key = list(self.buttons)[new_index]
                new_selected_button = new_index, key
                self.buttons[key].select()
                self.generate_description_surf()

        if new_selected_button:
            if self.selected_button:
                self.buttons[self.selected_button[1]].selected = False
            self.selected_button = new_selected_button

        btn = self.buttons[self.selected_button[1]]
        if self.game.inputs['pressed'].get('space') or self.game.inputs['pressed'].get('/'):
            btn.click()
        if btn.clicked:
            btn.bg = Animation.img_db['button_disabled']
            player_1 = self.game.game_map.level.player_1
            player_2 = self.game.game_map.level.player_2
            btn_name = self.selected_button[1]

            if btn_name == 'done':
                self.game.game_map.level.hide_shop()
                return

            btn.disable()
            if btn_name == 'double_jump':
                player_1.enable_double_jump()
            elif btn_name == 'high_jump':
                player_1.jump_force = 8
            elif btn_name == 'sprint':
                player_1.x_accel = 1
                player_1.x_max = 5
            elif btn_name == 'big_bubble':
                player_2.bubble_name = 'big_bubble'
                player_2.bubble_size = 21
            elif btn_name == 'kill_reset':
                player_2.kill_reset = True


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

        if self.description_surf:
            x = t1 * (1-self.buttons[self.selected_button[1]].unselect_timer.ratio)
            description_x = easing.lerp(config.GAME_SIZE[0],
                                        config.GAME_SIZE[0] - 300,
                                        easing.ease_in_out_quad(x))
            surf.blit(self.description_surf,
                      (description_x, 300))

        i = 0
        for key, button in self.buttons.items():
            btn_x = easing.lerp(config.GAME_SIZE[0], config.GAME_SIZE[0]-140-i*4, easing.ease_out_back(t2))
            button.rect.x = btn_x
            offset_x = easing.lerp(0, -70, easing.ease_out_back(1-button.unselect_timer.ratio))
            button.render(surf, offset=(offset_x, 0))
            i += 1

        title_x = easing.lerp(config.GAME_SIZE[0], 455, easing.ease_out_back(t1))
        surf.blit(Animation.img_db['shop_title'], (title_x, 10))

class Button:
    
    presets = {
        'basic': {
            'colors': {'border': [91, 77, 76], 
                       'fill': [151, 134, 125], 
                       'text': [240, 240, 240] }
        },
        'disabled': {
            'colors': {'border': [91, 77, 76], 
                       'fill': [151, 134, 125], 
                       'text': [240, 240, 240] }
        },
    }

    PRICE_SPACE = 20
    
    def __init__(self, rect: pygame.Rect, text, preset, price, bg=None, click_sound=None, description=''):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.preset = preset
        self.price = price
        self.selected = False
        self.clicked = False
        self.released = False
        self.disabled = False
        if bg is None: bg = Animation.img_db['button']
        self.bg = bg
        self.description = description
        self.description = 'Button description here waokeoaskdo '
        self.generate_surf()
        self.unselect_timer = Timer(8, done=True)
        self.click_sound = click_sound

    def disable(self):
        self.disabled = True
        self.generate_surf()

    def enable(self):
        self.disabled = False
        self.generate_surf()

    def generate_surf(self):

        s = pygame.Surface(pygame.Vector2(self.bg.get_size()) + (self.PRICE_SPACE, 0))
        s.blit(self.bg, (self.PRICE_SPACE, 0))
        s.set_colorkey((0,0,0))

        text_img = fonts[self.presets[self.preset].get('font', 'shop')].get_surf(self.text, color=self.colors['text'])
        y = 0.5*(s.get_height()-text_img.get_height())
        s.blit(text_img, (16 + self.PRICE_SPACE, y))
        self.surf = s
        
        if not self.disabled and not self.text == 'Done':
            s.blit(Animation.img_db['flake_ui'], (0, 3))

            font = fonts[self.presets[self.preset].get('font', 'basic')]
            price_img = font.get_surf(f'{self.price}', color=colors.BLACK)
            price_pos = (8, s.get_height()*0.5) - 0.5*pygame.Vector2(price_img.get_size())
            s.blit(price_img, price_pos + pygame.Vector2(0, 1))
            s.blit(price_img, price_pos + pygame.Vector2(0, -1))
            s.blit(price_img, price_pos + pygame.Vector2(1, 0))
            s.blit(price_img, price_pos + pygame.Vector2(-1, 0))

            price_img = font.get_surf(f'{self.price}', color=self.colors['text'])
            s.blit(price_img, price_pos)

        
    def update(self, inputs, select_sound='select.wav', click_sound='click.wav', ignore_mouse=False):
        click_sound = self.click_sound

        self.clicked = False
        if self.rect.collidepoint(inputs.get('game_mouse_pos')) and not ignore_mouse:
            self.select(select_sound)
            if inputs['pressed'].get('mouse1'):
                self.click()
            # else:
            #     self.selected = False



        if self.selected:
            if self.unselect_timer.frame:
                self.unselect_timer.frame -= 1
                self.unselect_timer.done = False
        else:
            self.unselect_timer.update()

        # self.generate_surf()

    def click(self):
        if self.disabled: return
        self.clicked = True
        sfx.sounds[self.click_sound].play()

    def select(self, select_sound='select.wav'):
        if not self.selected:
            if select_sound: sfx.sounds[select_sound].play()
        self.selected = True

                
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

