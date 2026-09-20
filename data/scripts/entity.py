import pygame
from math import atan, pi
from pygame import Vector2
from .animation import Animation
    
class Entity:
    def __init__(self, pos, name, action=None, collision_mode='hard'):
        self.real_pos = Vector2(pos)
        self.name = name
        self.animation = Animation(name, action)
        self.flip = [False, False]
        self.is_solid = True
        self.stop_on_collision = True
        self.collision_mode = collision_mode

    @property
    def pos(self):
        return Vector2(int(self.real_pos[0]), int(self.real_pos[1]))

    def change_pos(self, change_vec):
        # Did not want to use a setter method because it wouldn't be
        # called if you only touch one axis (like pos.x += x)
        
        # self._real_pos = self.pos + change_vec 
        if change_vec.x:
            self.real_pos.x = self.pos.x + change_vec.x
        if change_vec.y:
            self.real_pos.y = self.pos.y + change_vec.y

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(*(self.animation.rect.topleft + self.pos), *self.animation.rect.size)

    @property
    def img(self) -> pygame.Surface:
        return self.animation.img

    def update(self):
        return self.animation.update()

    def render(self, surf, offset=(0,0)):
        # pygame.draw.rect(surf, (255, 0, 0), self.rect)
        render_pos = self.pos + offset

        surf.blit(self.img, render_pos)
        # try:
        #     pygame.draw.rect(surf, (255, 0, 0), (self.rect.x + offset[0],
        #                                          self.rect.y + offset[1],
        #                                          self.rect.w,
        #                                          self.rect.h), 1)
        # except KeyError: pass

    def __repr__(self):
        return f'<{self.name}>'

    def on_collision(self, entity): pass

class PhysicsEntity(Entity):

    def __init__(self, vel=(0, 0), acceleration=(0, 0), max_vel=9999, collision_mode='hard', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vel = Vector2(vel)
        self.acceleration = Vector2(acceleration)
        self.max_vel = max_vel
        self.collision_mode = collision_mode
        self.collision_directions = {'up': False,
                                     'right': False,
                                     'down': False,
                                     'left': False}
        self.collided_tiles = set()

    @property
    def angle(self):
        angle = self.vel.angle_to(Vector2(1, 0))
        return angle

    def update(self, rects=None):
        output = super().update()

        self.collided_tiles = set()

        self.move(rects)
        self.vel += self.acceleration
        if self.vel.length() > self.max_vel:
            self.vel.scale_to_length(self.max_vel)

        return output

    def move(self, rects):
        if not rects:
            self.real_pos += self.vel
            return

        self.collision_directions = {'up': False,
                                     'right': False,
                                     'down': False,
                                     'left': False}

        for axis in range(2):
            self.resolve_collisions(axis, rects)

        for tile in self.collided_tiles:
            tile.on_collision(self)
            self.on_collision(tile)

    def resolve_collisions(self, axis, rects):
        # NOTE: Instead of breaking when finding tiles, it can also be useful
        # to append all collided tiles to the collisions directions
        self.real_pos[axis] += self.vel[axis]
        if self.collision_mode not in ('hard', 'soft_tracked'): return
        direction = None
        for tile in rects:
            rect = tile.rect
            if hasattr(tile, 'coord'):
                collide_condition = self.handle_coord_collision(tile)
            else:
                collide_condition = self.rect.colliderect(rect)
            if collide_condition:
                if axis == 0:
                    if self.vel[0] > 0:
                        delta = self.rect.right - rect.left
                        direction = 'right'
                    elif self.vel[0] < 0:
                        delta = self.rect.left - rect.right
                        direction = 'left'
                    else:
                        delta = 0
                        print(f'[WARNING] {self} Didn\'t resolve collision last frame or rect changed sizes ({axis=})')
                    if self.stop_on_collision and tile.collision_mode=='hard': self.vel[axis] = 0
                elif axis == 1:
                    if self.vel[1] < 0:
                        delta = self.rect.top - rect.bottom
                        direction = 'up'
                    elif self.vel[1] > 0:
                        delta = self.rect.bottom - rect.top
                        direction = 'down'
                    else:
                        delta = 0
                        print(f'[WARNING] {self} Didn\'t resolve collision last frame or rect changed sizes ({axis=})')
                    if self.stop_on_collision and tile.collision_mode=='hard': self.vel[axis] = 0

                if tile.collision_mode == 'hard':
                    v = Vector2(0, 0)
                    v[axis] = delta
                    if tile.is_solid:
                        self.change_pos(-v)

                    if direction:
                        self.collision_directions[direction] = True
                self.collided_tiles.add(tile)
                return

    def handle_coord_collision(self, tile):
        return self.rect.colliderect(tile.rect)

