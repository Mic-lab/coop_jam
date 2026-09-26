import random
import pygame
from . import enemies
from .timer import Timer
from abc import abstractmethod



class Wave:

    def __init__(self, game):
        self.game = game
        self.t = 0
        self.done_spawning = False

    def update(self):
        if self.done_spawning: return
        self.spawn_enemies()
        self.t += 1

    def spawn_enemy(self, Enemy: enemies.Fish, directions=(0, 1)):
        vel = pygame.Vector2(random.randint(10, 30), 0)
        vel.rotate_ip(random.randint(-30, 30))

        if random.choice(directions):
            x = 100
        else:
            x = 900
            vel.x *= -1
        y = 100
        enemy = Enemy(self.game, pos=(x, y), vel=vel)
        self.game.game_map.level.enemies.append(enemy)

    @abstractmethod
    def spawn_enemies(self):
        pass

class Wave1(Wave):

    def __init__(self, game):
        super().__init__(game)
        self.max_enemies = 30
        self.enemies_spawned = 0

    def spawn_enemies(self):
        if self.t % 60 == 0:
            # if random.randint(0,1):
            #     e = enemies.DashFish
            # else:
            #     e = enemies.NormalFish
            e = enemies.BigFish
            self.spawn_enemy(e, directions=[1])
            self.enemies_spawned += 1
            if self.enemies_spawned == self.max_enemies:
                self.done_spawning = True


class WaveManager:

    def __init__(self, game):
        self.game = game
        self.wave_index = 0
        self.waves = (
                Wave1(game),
                Wave1(game),
                Wave1(game),
                )
        self.wave_end_timer = Timer(120, done=True)

    @property
    def wave(self):
        return self.waves[self.wave_index]

    def update(self):
        self.wave.update()
        level = self.game.game_map.level

        wave_complete = self.wave.done_spawning and not level.enemies
        if wave_complete:
            if not self.old_wave_complete:
                self.wave_end_timer.reset()
                pygame.mixer_music.fadeout(2000)
        self.old_wave_complete = wave_complete

        timer_done_old = self.wave_end_timer.done
        self.wave_end_timer.update()
        timer_done_new = self.wave_end_timer.done
        if timer_done_new and not timer_done_old:
            self.on_wave_complete()

    def on_wave_complete(self):
        level = self.game.game_map.level
        level.show_shop()
        level.combo_manager.end_combo()

    def start_next_wave(self):
        if self.wave_index == len(self.waves) - 1:
            print('done')
        else:
            self.wave_index += 1
