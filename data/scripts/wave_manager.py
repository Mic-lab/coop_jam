import random
from . import enemies
from abc import abstractmethod



class Wave:

    def __init__(self, game):
        self.game = game
        self.t = 0

    def update(self):
        self.spawn_enemies()
        self.t += 1

    def spawn_enemy(self, Enemy: enemies.Fish):
        x = 100
        y = 100
        enemy = Enemy(self.game, pos=(x, y))
        self.game.game_map.level.enemies.append(enemy)

    @abstractmethod
    def spawn_enemies(self):
        pass

class Wave1(Wave):

    def spawn_enemies(self):
        if self.t % 30 == 0:
            if random.randint(0,1):
                e = enemies.DashFish
            else:
                e = enemies.NormalFish
            self.spawn_enemy(e)


class WaveManager:

    def __init__(self, game):
        self.game = game
        self.wave_index = 0
        self.waves = (
                Wave1(game),
                )

    @property
    def wave(self):
        return self.waves[self.wave_index]

    def update(self):
        self.wave.update()
