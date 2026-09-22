import pygame
from pygame import Vector2 as Vec2
from . import colors
from .particle import ParticleGenerator, Particle
from .players import Player, Player2
from .entity import PhysicsEntity
import math
import random

class Fish(PhysicsEntity):

    SPEED = 2
    ACCELERATION = 0.1

    ANGLE_ROUNDING = 1
    cache = {}

    def __init__(self, game, *args, **kwargs):
        self.game = game
        self.angled = True
        super().__init__(*args, **kwargs)
        self.dead = False
        self.collision_mode = 'soft_tracked'
        self.coord = self.pos - 0.5*Vec2(self.img.get_size())
        self.t = 0
        self.tag = 'enemy'

    def do_behavior(self):
        pass

    def update(self, rects=None):
        self.do_behavior()

        super().update(rects)

        self.coord = self.pos - 0.5*Vec2(self.img.get_size())

        if self.vel[0] < 0:
            self.animation.flip[0] = True
        elif self.vel[0] > 0:
            self.animation.flip[0] = False

        return {
                'remove': self.dead
                }

    @property
    def angle(self):
        angle = super().angle
        if self.vel[0] > 0:
            return angle
        return 180+angle

    def on_collision(self, entity):
        # if not isinstance(entity, Player): return
        #


        hit = False
        if isinstance(entity, Player):
            if isinstance(entity, Player2) and entity.being_pulled:
                print('ON COLLISION WITH P2')
                self.die(entity.vel)
            else:
                hit = True

        if hit:
            pass


        return super().on_collision(entity)

    def die(self, vel):
        self.dead = True
        self.game.game_map.level.particle_gens.append(
        ParticleGenerator.from_template(
                self.center,
                'kill',
                # rate=1,
                # vel_randomness=9,
                base_particle=lambda: Particle(action='kill', vel=vel*0.5, angled=True)
                )
        )

        self.game.game_map.level.particle_gens.append(
                ParticleGenerator.from_template(
                    self.center,
                    'dust',
                    base_particle=lambda: Particle(action='dust', vel=vel*2, angled=True, friction=0.92)
                    )
                )

    @property
    def rounded_angle(self):
        return round(self.angle / self.ANGLE_ROUNDING) * self.ANGLE_ROUNDING

    @property
    def img(self):
        img = super().img
        key = (self.name, self.rounded_angle, self.animation.animation_frame)
        if cached_img := self.cache.get(key) and 0:
            return cached_img
        
        img = pygame.transform.rotate(img, self.rounded_angle)
        self.cache[key] = img
        return img

    def render(self, surf, offset):
        surf.blit(
                self.img,
                self.coord + offset,
                )
        # pygame.draw.rect(surf, (0, 255, 255), (*self.coord+offset, 3, 3))

    @property
    def center(self):
        return self.coord+0.5*Vec2(self.img.get_size())


class NormalFish(Fish):

    def do_behavior(self):
        player_1 = self.game.game_map.level.player_1
        player_2 = self.game.game_map.level.player_2

        if player_2.being_pulled:
            player = player_1

        else:
            dist_1 = Vec2(self.coord - player_1.rect.center).length()
            dist_2 = Vec2(self.coord - player_2.rect.center).length()
            if dist_1 < dist_2: player = player_1
            else: player = player_2

        accel = (self.coord - player.rect.center)
        accel = (player.rect.center - self.pos)

        if accel.length() > self.ACCELERATION:
            accel.scale_to_length(self.ACCELERATION)
        self.vel += accel
        if self.vel.length() > self.SPEED:
            self.vel.scale_to_length(self.SPEED)


class DashFish(Fish):

    ACCELERATION = 0.08

    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.t = 0

    def do_behavior(self):
        player_1 = self.game.game_map.level.player_1
        player_2 = self.game.game_map.level.player_2

        if player_2.being_pulled:
            player = player_1

        else:
            dist_1 = Vec2(self.coord - player_1.rect.center).length()
            dist_2 = Vec2(self.coord - player_2.rect.center).length()
            if dist_1 < dist_2: player = player_1
            else: player = player_2

        accel = (self.coord - player.rect.center)
        accel = (player.rect.center - self.pos)

        if accel.length() > self.ACCELERATION:
            accel.scale_to_length(self.ACCELERATION * (1+(math.sin((2/60)*self.t))))
        self.vel += accel
        self.vel *= 0.98

        self.t += random.randint(1, 3)
