from pygame import Vector2 as Vec2
from .entity import PhysicsEntity, Entity
from .timer import Timer
import random
from . import sfx
from .particle import ParticleGenerator

def scale_to_length(vector, length):
    if not vector: return vector
    vector.scale_to_length(length)

class Player(PhysicsEntity):
    
    BOUNCE = 0.9
    GRAVITY_UP = 0.15
    GRAVITY_DOWN = 0.9

    GRAVITY_UP = 0.2
    GRAVITY_DOWN = 0.5

    def __init__(self, game, *args, **kwargs):
        self.game = game
        super().__init__(*args, **kwargs)
        self.grounded = False
        self.jumping = False
        self.jump_descent = True
        self.jump_timer = Timer(12, done=True)  # Jump buffer
        self.grounded_timer = Timer(6, done=True)  # Coyote time
        self.jump_force = 6
        
        self.wings = None
        self.show_wings = False
        self.did_double_jump = False

        self.can_double_jump = False
        # self.enable_double_jump()

    def enable_double_jump(self):
        self.can_double_jump = True
        self.wings = Entity((0, 0), 'wings', action='idle')


    @property
    def jump_rising(self):
        return self.jumping and self.vel[1] < 0

    def update(self, actions, rects=None):
        if actions['down_pressed']:
            self.force_pass = True
        elif actions['down_released']:
            self.force_pass = False

        started_jump = False
        if actions['jump_pressed']:
            self.jump_timer.reset()
        if not self.jump_timer.done:
            if (self.grounded or not self.grounded_timer.done) and not self.jumping: 
                self.start_jump()
                started_jump = True
                sfx.sounds['jump.wav'].play()

        if actions['jump_pressed'] and not started_jump:
            if not self.grounded and self.can_double_jump and not self.did_double_jump:
                print('DOUBLE JUMPING')
                self.show_wings = True
                self.wings.animation.set_action('idle', reset=True)
                self.did_double_jump = True
                self.start_jump()
                sfx.sounds['double_jump.wav'].play()

        if actions['jump_released']:
            self.jump_release()


        if actions['move_left']:
            self.vel[0] -= 0.5
        if actions['move_right']:
            self.vel[0] += 0.5

        self.vel[0] *= 0.9
        self.vel[0] = max(-3, min(3, self.vel[0]))

        if self.vel[1] > 0:
            self.jump_descent = True
        if self.jumping and not self.jump_descent:
            self.vel[1] += self.GRAVITY_UP
        else:
            self.vel[1] += self.GRAVITY_DOWN

        self.jump_timer.update()
        self.grounded_timer.update()

        super().update(rects)

        # NOTE: idk if this activates at every frame cause gravity's intensity is subpixel
        if self.collision_directions['down']:
            self.grounded = True
            self.did_double_jump = False
            if not started_jump:
                # self.vel[1] = 0
                self.jumping = False
        else:
            if self.grounded:
                self.grounded = False
                self.grounded_timer.reset()
        #
        # if self.collision_directions['up']:
        #     self.vel[1] = 0
        #
        # if self.collision_directions['left'] or self.collision_directions['right']:
        #     self.vel[0] = 0

        if self.show_wings:
            self.wings.animation.flip[0] = self.animation.flip[0]
            self.wings.real_pos = self.rect.topleft - Vec2(self.wings.animation.rect.topleft)
            if self.wings.update():
                self.show_wings = False

    def render(self, surf, offset=(0, 0)):
        if self.show_wings:
            self.wings.render(surf, offset)
        super().render(surf, offset)

    def jump_release(self):
        if self.jumping and self.vel[1] < 0:
            self.vel[1] *= 0.5
            self.jump_descent = True

    def start_jump(self):
        self.jump_descent = False
        self.vel[1] = -4
        self.vel[1] = -self.jump_force
        self.jumping = True

        self.jump_timer.reset(done=True)
        self.grounded_timer.reset(done=True)

        self.game.game_map.level.particle_gens.append(
                ParticleGenerator.from_template(
                    self.rect.midbottom,
                    'smoke',
                    )
                )

class Player1(Player):

    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.pull_request_timer = Timer(60, done=True)

    def update(self, rects=None):

        # if self.game.inputs['pressed'].get('e'):
        #     self.pull_request_timer.reset()

        actions = {
                'jump_pressed': self.game.inputs['pressed'].get('w'),
                'jump_released': self.game.inputs['released'].get('w'),
                'move_left': self.game.inputs['held'].get('a'),
                'move_right': self.game.inputs['held'].get('d'),
                'down_pressed': self.game.inputs['pressed'].get('s'),
                'down_released': self.game.inputs['released'].get('s'),
                }

        self.pull_request_timer.update()

        super().update(actions, rects)

        if self.vel[0] < 0:
            self.animation.flip[0] = True
        elif self.vel[0] > 0:
            self.animation.flip[0] = False




class Player2(Player):

    PULL_SPEED = 5
    PULL_SPEED = 12
    
    PULL_ACCELERATION = 0.14
    BUBBLE_GRAVITY = 0.1
    BUBBLE_CONTROL = 0.09  # shouldnt be more than gravity, otherwise u can fly up

    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.being_pulled = False
        self.pull_request_timer = Timer(120)
        self.bubble = None
        self.kill = 0

    def update(self, rects=None):
        level = self.game.game_map.level
        self.kills = 0
        player_1 = self.game.game_map.level.player_1

        actions = {
                'jump_pressed': self.game.inputs['pressed'].get('up'),
                'jump_released': self.game.inputs['released'].get('up'),
                'move_left': self.game.inputs['held'].get('left'),
                'move_right': self.game.inputs['held'].get('right'),
                'down_pressed': self.game.inputs['pressed'].get('down'),
                'down_released': self.game.inputs['released'].get('down'),
                }

        # if actions.get('move_left'):
        #     level.shop.hide()
        # elif actions.get('move_right'):
        #     level.shop.show()

        if self.game.inputs['pressed'].get('/') and not self.being_pulled:
        # if self.game.inputs['pressed'].get('/'):
            self.pull_request()

        if not self.pull_request_timer.done:  # TMP
            # if not player_1.pull_request_timer.done:
            self.force_pass = True
            self.being_pulled = True
            vel = (Vec2(player_1.rect.center) - self.rect.center)

            scale_to_length(vel, self.PULL_SPEED)
            # vel *= 0.8

            self.vel = vel
            self.bubble = Entity((0, 0), 'bubble', 'idle')

            self.pull_request_timer.reset(done=True)
            player_1.pull_request_timer.reset(done=True)

        if self.being_pulled:
            acceleration = (Vec2(player_1.rect.center) - self.rect.center)
            scale_to_length(acceleration, self.PULL_ACCELERATION)
            # self.vel += acceleration
            
            # if self.vel.length() > self.PULL_SPEED:
            #     scale_to_length(self.vel, self.PULL_SPEED)
            self.vel[1] += self.BUBBLE_GRAVITY
            self.vel *= 0.97



        self.pull_request_timer.update()

        # super().update(actions, rects, normal_collisions=not self.being_pulled)
        if self.being_pulled:
            self.collision_mode = 'hard'

            vel_change = Vec2()
            if self.game.inputs['held'].get('up'):
                vel_change[1] -= 1
            if self.game.inputs['held'].get('down'):
                vel_change[1] += 1
            if self.game.inputs['held'].get('right'):
                vel_change[0] += 1
            if self.game.inputs['held'].get('left'):
                vel_change[0] -= 1

            scale_to_length(vel_change, self.BUBBLE_CONTROL)
            self.vel += vel_change

            PhysicsEntity.update(self, rects)
        else:
            self.collision_mode = 'hard'
            super().update(actions, rects)

        '''
        if self.being_pulled:
            # input(self.collision_directions)
            if (Vec2(self.rect.center) - player_1.rect.center).length() < 10:
                self.reset_pull()
        '''

        if self.bubble:
            done = self.bubble.update()
            if done and self.bubble.animation.action == 'pop':
                self.bubble = None

        if self.vel[0] < 0:
            self.animation.flip[0] = True
        elif self.vel[0] > 0:
            self.animation.flip[0] = False


    def pull_request(self):
        self.pull_request_timer.reset()

    def render(self, surf, offset):
        super().render(surf, offset)
        if self.bubble:
            self.bubble.real_pos = self.rect.center - 0.5*Vec2(self.bubble.rect.size)
            self.bubble.render(surf, offset)

    def on_collision(self, entity):
        if entity.tag == 'enemy':
            if self.being_pulled:
                self.game.game_map.level.combo_manager.add_kills(1)
                sfx.sounds[f'kill_{random.randint(1, 4)}.wav'].play()
                # self.vel *= -0.3
                self.game.end_freeze(3)
        else:
            pass
            # print(f'{self.force_pass=}')
            if self.being_pulled:
                self.reset_pull()

        return super().on_collision(entity)

    def reset_pull(self):
        self.game.game_map.level.combo_manager.end_combo()
        sfx.sounds[f'pop.wav'].play()
        self.being_pulled = False
        self.bubble.animation.set_action('pop')
        self.force_pass = False

    BUBBLE_SIZE = 16
    # BUBBLE_SIZE = 64

    def handle_coord_collision(self, tile):
        return (Vec2(self.rect.center) - tile.center).length() < (self.BUBBLE_SIZE+5)
