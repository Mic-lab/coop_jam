import pygame
from pygame import Vector2 as Vec2
from .entity import Entity
from . import config
from .players import Player1, Player2

class Level:

    def __init__(self, game_map):
        self.game_map = game_map
        self.load()

    def load(self):

        file_content = '''
       00000000000


0000000000000000000000000
        '''

        self.player_1 = Player1(self.game_map.game, name='side', pos=(0, -30), action='idle')
        self.player_2 = Player2(self.game_map.game, name='side', pos=(30, -30), action='idle')

        tiles = []

        max_x = -1

        y = 0
        for line in file_content.splitlines():
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
        return -Vec2(self.player_1.rect.center) + 0.5*config.GAME_SIZE

    def update(self):
        self.player_1.update(self.tiles)
        self.player_2.update(self.tiles)
        for tile in self.tiles:
            tile.update()

        self.offset += 0.5*(self.desired_offset-self.offset)

    def render(self, surf):
        rounded_offset = Vec2(int(self.offset[0]), int(self.offset[1]))
        self.player_1.render(surf, offset=rounded_offset)
        self.player_2.render(surf, offset=rounded_offset)
        for tile in self.tiles:
            tile.render(surf, offset=rounded_offset)

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
