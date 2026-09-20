import pygame
from pygame import Vector2 as Vec2

from data.scripts.enemies import Enemy
from .entity import Entity
from . import config
from .players import Player1, Player2
from .particle import ParticleGenerator

class Level:

    def __init__(self, game_map):
        self.game_map = game_map
        self.load()

    def load(self):

        level_content = '''



0000000000000



0000000000000



          000000000000000000




      000000000000
    


0000000000000000000000000
        '''

        self.particle_gens = []
        self.player_1 = Player1(self.game_map.game, name='side', pos=(0, -30), action='idle')
        self.player_2 = Player2(self.game_map.game, name='side', pos=(30, -30), action='idle')
        self.enemies = [
                Enemy(self.game_map.game, pos=(100, 0), name='ghost', action='idle')
                ]

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
        entities = self.tiles + self.enemies
        self.player_1.update(entities)
        self.player_2.update(entities)
        for tile in self.tiles:
            tile.update()
        new_enemies = []
        for enemy in self.enemies:
            output = enemy.update()
            if output.get('remove'):
                continue
            new_enemies.append(enemy)
        self.enemies = new_enemies

        self.offset += 0.5*(self.desired_offset-self.offset)

        if self.game_map.t % 120 == 0:
            self.enemies.append(
                Enemy(self.game_map.game, pos=(100, 0), name='ghost', action='idle')
                    )

        ParticleGenerator.update_generators(self.particle_gens)


    def render(self, surf):
        rounded_offset = Vec2(int(self.offset[0]), int(self.offset[1]))
        self.player_1.render(surf, offset=rounded_offset)
        self.player_2.render(surf, offset=rounded_offset)
        for tile in self.tiles:
            tile.render(surf, offset=rounded_offset)
        for enemy in self.enemies:
            enemy.render(surf, offset=rounded_offset)

        for gen in self.particle_gens:
            gen.render(surf, offset=rounded_offset)

class GameMap:

    def __init__(self, game):
        self.game = game
        self.level = Level(self)
        self.t = 0

    def update(self):
        self.level.update()
        self.t += 1

    def render(self, surf):
        self.level.render(surf)

class Tile(Entity):

    def __init__(self, pos, name, action=None):
        super().__init__(pos, name, action)
