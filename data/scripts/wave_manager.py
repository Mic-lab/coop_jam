import random
import pygame
from . import enemies
from .entity import Entity, PhysicsEntity
from . import config, colors, sfx
from .easing import lerp, ease_out_back
from .timer import Timer
from .font import fonts
from .flake_indicator import Flake
from abc import abstractmethod



class Wave:

    PAN = 8

    def __init__(self, game, num):
        self.game = game
        self.num = num
        self.t = 0
        self.done_spawning = False

        self.text = fonts['title'].get_surf(f'Wave {num}')
        self.text_bg = pygame.Surface((config.GAME_SIZE[0],
                                       fonts['title'].obj.get_height()+2*self.PAN))
        self.text_bg.fill(colors.DARK_RED)
        self.start_timer = Timer(120)

    def spawn_flake(self):
        flake = Flake(self.game, pos=(0+random.randint(1, 300), 0))
        self.game.game_map.level.flakes.append(flake)

    def update(self):
        was_done = self.start_timer.done
        self.start_timer.update()
        if self.done_spawning: return

        if self.start_timer.done:
            if not was_done:
                pygame.mixer_music.set_volume(0.7)
                sfx.play_music('song.wav')

            self.spawn_enemies()

            if self.t % (1*60) == 0:
                self.spawn_flake()

            self.t += 1

    def spawn_enemy(self, Enemy: enemies.Fish, directions=(0, 1)):
        vel = pygame.Vector2(random.randint(10, 30), 0)
        vel.rotate_ip(random.randint(-40, 40))

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

    def render(self, surf):

        pos = (0, lerp(100, 0, 1-ease_out_back(1-self.start_timer.ratio)))

        self.text_bg.set_alpha((1-self.start_timer.ratio)*255)
        surf.blit(self.text_bg, pos)
        surf.blit(self.text,
                  (0.5*(config.GAME_SIZE[0]-self.text.get_width()),
                   pos[1]+self.PAN)
                  )


class Wave1(Wave):

    def __init__(self, game, n):
        super().__init__(game, n)
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

class Wave2(Wave):

    def __init__(self, game, n):
        super().__init__(game, n)
        self.max_enemies = 120
        self.enemies_spawned = 0

    def spawn_enemies(self):
        if self.t % 100 == 0:
            if random.randint(0,1):
                e = enemies.BigFish
            else:
                e = enemies.NormalFish
            self.spawn_enemy(e, directions=[1, 0])
            self.enemies_spawned += 1
            if self.enemies_spawned == self.max_enemies:
                self.done_spawning = True


class WaveManager:

    def __init__(self, game):
        self.game = game
        self.wave_index = 0
        self.waves = (
                None,
                Wave1(game,1),
                Wave2(game,2),
                Wave2(game,3),
                )
        self.wave_end_timer = Timer(120, done=True)

    @property
    def wave(self):
        return self.waves[self.wave_index]

    def update(self):
        if not self.wave: return

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
        pygame.mixer_music.fadeout(1000)
        if self.wave_index == len(self.waves) - 1:
            print('done')
        else:
            self.wave_index += 1

    def render(self, surf):
        if not self.wave: return
        self.wave.render(surf)


