import pygame
from pygame import Vector2 as Vec2
from .entity import Entity
from . import config
from .player import Player

class Level:

    def __init__(self, game_map):
        self.game_map = game_map
        self.load()

    def load(self):

        file_content = '''
0000000
0000000
        '''

        self.player_1 = Player(name='side', pos=(0, 0), action='idle')
        self.player_2 = Player(name='side', pos=(10, 0), action='idle')

        tiles = []

        max_x = -1

        y = 0
        for line in file_content.splitlines():
            if not line: continue
            for x, c in enumerate(line):
                if x > max_x: max_x = x
                pos = (x*config.TILE_SIZE[0], y*config.TILE_SIZE[1])
                if c == '0':
                    tile = Tile(pos, 'ground')
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
        return self.player_1.rect.center + 0.5*config.GAME_SIZE

    def update(self):
        self.player_1.update()
        self.player_2.update()
        for tile in self.tiles:
            tile.update()

        self.offset += 0.5*(self.desired_offset-self.offset)

    def render(self, surf):
        self.player_1.render(surf, offset=self.offset)
        self.player_2.render(surf, offset=self.offset)
        for tile in self.tiles:
            tile.render(surf, offset=self.offset)

class GameMap:

    def __init__(self, game):
        self.game = game
        self.level = Level(self)

    def update(self):
        self.level.update()

    def render(self, surf):
        self.level.render(surf)

class Tile(Entity):

    def __init__(self, pos, name, action=None):
        super().__init__(pos, name, action)
