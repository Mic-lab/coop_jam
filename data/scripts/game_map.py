import pygame
import random
from pygame import Vector2 as Vec2

from data.scripts import enemies
from .entity import Entity
from . import config, sfx
from .players import Player1, Player2
from .particle import ParticleGenerator
from .mgl import shader_handler
from .combo_manager import ComboManager
from .orb import Orb, HpBar
from .shop import Shop
from .wave_manager import WaveManager
from .animation import Animation
from .flake_indicator import FlakeIndicator

class Level:

    def __init__(self, game_map):
        self.game_map = game_map
        self.game = self.game_map.game
        self.load()

    def load(self):

        self.load_tiles()

        self.tutorial = True
        pygame.mixer_music.set_volume(0.5)
        sfx.play_music('tutorial.wav')

        self.combo_manager = ComboManager(self)
        self.flake_indicator = FlakeIndicator()
        self.wave_manager = WaveManager(self.game)

        self.shop = Shop(self.game_map.game)

        self.particle_gens = []
        x = ((self.size[0]+0.5)*config.TILE_SIZE[0])*0.5
        self.player_1 = Player1(self.game_map.game, name='side', pos=(x, -30), action='idle')
        self.player_2 = Player2(self.game_map.game, name='player_2', pos=(x, -30), action='idle')
        self.orb = Orb(self, (450, 74))
        self.hp_bar = HpBar((0, 30), 20)
        self.hp_bar.real_pos[0] = 0.5*(config.GAME_SIZE[0] - self.hp_bar.img.get_width())
        self.enemies = []
        self.flakes = []
        self.offset = self.desired_offset
        self.moving_surfs = []


    def load_tiles(self):
        level_content = '''

p
p                      
p                                       
p     11111     11111                     11111     11111
p
p                                                            p
p   1111111111111111111                 1111111111111111111  p
p                                                            p
p                                                            p
00000000000000000000000000000000000000000000000000000000000000
        '''
        tiles = []
        max_x = -1
        y = 0
        for line in level_content.splitlines():
            # if not line: continue
            for x, c in enumerate(line):
                if x > max_x: max_x = x
                pos = (x*config.TILE_SIZE[0], y*config.TILE_SIZE[1])
                if c == '0':
                    tile = Tile(pos, 'ground', action='idle')
                    tiles.append(tile)
                if c == '1':
                    tile = Tile(pos, 'platform', action='idle', is_platform=True)
                    tiles.append(tile)
                if c == 'p':
                    tile = Tile(pos, 'portal', action='idle')
                    tiles.append(tile)
                elif c == ' ':
                    pass
                else:
                    pass
                    # raise KeyError
                x += 1
            y += 1
        self.tiles = tiles
        self.size = (max_x, y)

    @property
    def desired_offset(self):
        # return Vec2(self.player_1.rect.topleft)
        # return -Vec2(self.player_1.rect.center) + 0.5*config.GAME_SIZE
        return -1*(0.3*Vec2(self.player_1.rect.center)+0.3*Vec2(self.player_2.rect.center)+0.4*Vec2(self.orb.rect.center)) + 0.5*config.GAME_SIZE

    def show_shop(self):
        self.shop.show()
        pygame.mixer_music.set_volume(1)
        sfx.play_music('shop.wav')
        self.combo_manager.end_combo()
    
    def hide_shop(self):
        self.shop.hide()
        self.wave_manager.start_next_wave()


    def update(self):
        game = self.game_map.game

        if game.inputs['pressed'].get('space') and self.tutorial:
            self.tutorial = False
            self.wave_manager.start_next_wave()

        if game.inputs['pressed'].get('1'):
            self.show_shop()
        if game.inputs['pressed'].get('2'):
            self.hide_shop()


        if not self.shop.showing:
            entities = self.tiles + self.enemies
            self.player_1.update(entities)
            self.player_2.update(entities)
            for tile in self.tiles:
                tile.update()
            self.orb.update()
            self.hp_bar.update()

            self.wave_manager.update()

            new_enemies = []
            for enemy in self.enemies:
                output = enemy.update([self.orb])
                if output.get('remove'):
                    continue
                new_enemies.append(enemy)
            self.enemies = new_enemies

            new_flakes = []
            for flake in self.flakes:
                output = flake.update((self.player_1, *self.tiles))
                if output.get('remove'):
                    continue
                new_flakes.append(flake)
            self.flakes = new_flakes


        new_moving_surfs = []
        for moving_surf in self.moving_surfs:
            s = moving_surf['surf']
            s.set_alpha(s.get_alpha() - moving_surf['alpha_change'])
            if s.get_alpha() <= 0:
                break
            moving_surf['pos'] += moving_surf['vel']+Vec2(random.uniform(-1, 1), random.uniform(-1, 1))
            new_moving_surfs.append(moving_surf)
        self.moving_surfs = new_moving_surfs

        if self.hp_bar.val <= 0:
            self.restart()

        self.offset += 0.5*(self.desired_offset-self.offset)


        ParticleGenerator.update_generators(self.particle_gens)

        self.combo_manager.update()
        self.flake_indicator.update()
        self.shop.update()

    def restart(self):
        pygame.mixer_music.fadeout(1000)
        self.game.handler.transition_to(self.game.handler.states.Game)

    def render(self, surf):
        rounded_offset = Vec2(int(self.offset[0]), int(self.offset[1]))
        self.orb.render(surf, offset=rounded_offset)

        self.player_1.render(surf, offset=rounded_offset)
        self.player_2.render(surf, offset=rounded_offset)
        for tile in self.tiles:
            tile.render(surf, offset=rounded_offset)
        for enemy in self.enemies + self.flakes:
            enemy.render(surf, offset=rounded_offset)

        for gen in self.particle_gens:
            gen.render(surf, offset=rounded_offset)

        for moving_surf in self.moving_surfs:
            surf.blit(moving_surf['surf'], moving_surf['pos']+rounded_offset)

        if not self.tutorial:
            self.hp_bar.render(surf)

        self.combo_manager.render(surf, (0, 0))
        self.shop.render(surf)

        if not self.tutorial:
            self.flake_indicator.render(surf)

        if self.tutorial:
            img = Animation.img_db['tutorial']
            surf.blit(
                    Animation.img_db['tutorial'],
                    0.5*Vec2(config.GAME_SIZE) + rounded_offset + (0, -400)
                    )

        self.wave_manager.render(surf)

        shader_handler.vars['offset'] = self.offset

class GameMap:

    def __init__(self, game):
        self.game = game
        self.level = Level(self)
        self.t = 0

    def update(self):
        self.level.update()
        self.t += 1
        shader_handler.vars['t'] = self.t

    def render(self, surf):
        self.level.render(surf)

class Tile(Entity):

    def __init__(self, pos, name, action=None, is_platform=False):
        if is_platform:
            soft_directions = {'right', 'left', 'up'}
        else:
            soft_directions = None
        super().__init__(pos, name, action, soft_directions=soft_directions)
