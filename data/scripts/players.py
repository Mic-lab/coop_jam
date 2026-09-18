from pygame import Vector2 as Vec2
from .entity import PhysicsEntity
from .timer import Timer

class Player(PhysicsEntity):
    
    GRAVITY_UP = 0.2
    GRAVITY_DOWN = 0.4

    def __init__(self, game, *args, **kwargs):
        self.game = game
        super().__init__(*args, **kwargs)
        self.grounded = False
        self.jumping = False
        self.jump_timer = Timer(12, done=True)  # Jump buffer
        self.grounded_timer = Timer(12, done=True)  # Coyote time

    @property
    def jump_rising(self):
        return self.jumping and self.vel[1] < 0

    def update(self, actions, rects=None, allow_gravity=True):

        started_jump = False
        if actions['jump_pressed']:
            self.jump_timer.reset()
        if not self.jump_timer.done:
            if (self.grounded or not self.grounded_timer.done) and not self.jumping: 
                self.start_jump()
                self.jump_timer.reset(done=True)
                self.grounded_timer.reset(done=True)
                started_jump = True

        elif actions['jump_released']:
            self.jump_release()

        if actions['move_left']:
            self.vel[0] -= 0.5
        if actions['move_right']:
            self.vel[0] += 0.5

        if allow_gravity:
            self.vel[0] *= 0.9
            self.vel[0] = max(-3, min(3, self.vel[0]))

        # NOTE: idk if this activates at every frame cause gravity's intensity is subpixel
        if self.collision_directions['down']:
            self.grounded = True
            if not started_jump:
                self.vel[1] = 0
                self.jumping = False
        else:
            if self.grounded:
                self.grounded = False
                self.grounded_timer.reset()

        if self.collision_directions['up']:
            self.vel[1] = 0

        if self.vel[1] > 0: self.jump_descent = True
        if allow_gravity:
            if self.jumping and not self.jump_descent:
                self.vel[1] += self.GRAVITY_UP
            else:
                self.vel[1] += self.GRAVITY_DOWN

        self.jump_timer.update()
        self.grounded_timer.update()

        super().update(rects)

    def jump_release(self):
        if self.jumping and self.vel[1] < 0:
            self.vel[1] *= 0.5
            self.jump_descent = True

    def start_jump(self):
        self.jump_descent = False
        self.vel[1] = -5
        self.jumping = True


class Player1(Player):

    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.pull_request_timer = Timer(60, done=True)

    def update(self, rects=None):

        if self.game.inputs['pressed'].get('b'):
            self.pull_request_timer.reset()

        actions = {
                'jump_pressed': self.game.inputs['pressed'].get('v'),
                'jump_released': self.game.inputs['released'].get('v'),
                'move_left': self.game.inputs['held'].get('a'),
                'move_right': self.game.inputs['held'].get('d'),
                }

        self.pull_request_timer.update()

        super().update(actions, rects)



class Player2(Player):

    PULL_SPEED = 4
    PULL_ACCELERATION = 0.2

    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.being_pulled = False
        self.pull_request_timer = Timer(120)

    def update(self, rects=None):
        player_1 = self.game.game_map.level.player_1

        actions = {
                'jump_pressed': False,
                'jump_released': False,
                'move_left': False,
                'move_right': False,
                }

        if self.game.inputs['pressed'].get('m'):
            self.pull_request()

        if not self.pull_request_timer.done:
            if not player_1.pull_request_timer.done:
                self.being_pulled = True
                vel = (player_1.pos - self.pos)
                vel.scale_to_length(self.PULL_SPEED)
                self.vel = vel

        if self.being_pulled:
            # self.collision_mode = 'soft'
            acceleration = (player_1.pos - self.pos)
            acceleration.scale_to_length(self.PULL_ACCELERATION)
            self.vel += acceleration
            if self.vel.length() > self.PULL_SPEED:
                self.vel.scale_to_length(self.PULL_SPEED)

            if (Vec2(self.rect.center) - player_1.rect.center).length() < 10:
                self.being_pulled = False
                self.pull_request_timer.reset(done=True)
                player_1.pull_request_timer.reset(done=True)
        else:
            pass
            # self.collision_mode = 'hard'


        self.pull_request_timer.update()

        super().update(actions, rects, allow_gravity=not self.being_pulled)

    def pull_request(self):
        self.pull_request_timer.reset()
