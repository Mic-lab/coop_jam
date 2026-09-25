import pygame
import random
from pygame import Vector2 as Vec2

from data.scripts import enemies
from .entity import Entity
from . import config
from .players import Player1, Player2
from .particle import ParticleGenerator
from .mgl import shader_handler
from .combo_manager import ComboManager
from .orb import Orb, HpBar
from .shop import Shop
from .wave_manager import WaveManager

class Level:

    def __init__(self, game_map):
        self.game_map = game_map
        game = self.game_map.game
        self.load()
        self.combo_manager = ComboManager()
        self.wave_manager = WaveManager(game)

    def load(self):

        level_content = '''


                       
                                        


        00000000000000                      00000000000

     
     
000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        '''

        self.shop = Shop(self.game_map.game)
        self.shop.show()

        self.particle_gens = []
        self.player_1 = Player1(self.game_map.game, name='side', pos=(0, -30), action='idle')
        self.player_2 = Player2(self.game_map.game, name='player_2', pos=(30, -30), action='idle')
        self.orb = Orb(self, (400, 74))
        self.hp_bar = HpBar((0, 20), 20)
        self.hp_bar.real_pos[0] = 0.5*(config.GAME_SIZE[0] - self.hp_bar.rect.w)

        self.enemies = []
        # self.enemies = [
        #         enemies.NormalFish(self.game_map.game, pos=(100, 0), name='ghost', action='idle')
        #         ]

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
                elif c == ' ':
                    pass
                else:
                    raise KeyError
                x += 1
            y += 1

        self.tiles = tiles
        self.size = (max_x, y)


        self.offset = self.desired_offset

    @property
    def desired_offset(self):
        # return Vec2(self.player_1.rect.topleft)
        # return -Vec2(self.player_1.rect.center) + 0.5*config.GAME_SIZE
        return -0.5*(Vec2(self.player_1.rect.center)+self.player_2.rect.center) + 0.5*config.GAME_SIZE

    def update(self):
        game = self.game_map.game

        if game.inputs['pressed'].get('1'):
            self.shop.show()
        if game.inputs['pressed'].get('2'):
            self.shop.hide()


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

        self.offset += 0.5*(self.desired_offset-self.offset)


        ParticleGenerator.update_generators(self.particle_gens)

        self.combo_manager.update()
        self.shop.update()

    def render(self, surf):
        rounded_offset = Vec2(int(self.offset[0]), int(self.offset[1]))
        self.orb.render(surf, offset=rounded_offset)

        self.player_1.render(surf, offset=rounded_offset)
        self.player_2.render(surf, offset=rounded_offset)
        for tile in self.tiles:
            tile.render(surf, offset=rounded_offset)
        for enemy in self.enemies:
            enemy.render(surf, offset=rounded_offset)

        for gen in self.particle_gens:
            gen.render(surf, offset=rounded_offset)

        self.hp_bar.render(surf)

        self.combo_manager.render(surf, (0, 0))

        self.shop.render(surf)

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

    def __init__(self, pos, name, action=None):
        super().__init__(pos, name, action)
