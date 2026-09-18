from .entity import PhysicsEntity

class Player(PhysicsEntity):
    
    GRAVITY_UP = 0.2
    GRAVITY_DOWN = 0.4

    def __init__(self, game, *args, **kwargs):
        self.game = game
        super().__init__(*args, **kwargs)
        self.grounded = False
        self.jumping = False

    def update(self, rects=None):




        if self.vel[1] < 0:
            self.grounded = False
        # NOTE: This does NOT activate at every frame cause
        # gravity's intensity is subpixel
        # Also, I use elif because both conditions are true on the frame of jump.
        elif self.collision_directions['down']:
            self.vel[1] = 0
            self.grounded = True
            self.jumping = False


        if self.jumping:
            self.vel[1] += self.GRAVITY_UP

            if self.vel[1] > 0:
                self.jumping = False

        else:
            self.vel[1] += self.GRAVITY_DOWN

        super().update(rects)

    def jump_release(self):
        if self.jumping:
            self.vel[1] *= 0.5
            self.jumping = False

    def start_jump(self):
        if self.grounded:
            self.vel[1] -= 5
            self.jumping = True


class Player1(Player):

    def update(self, rects=None):
        if self.game.inputs['pressed'].get('v'):
            self.start_jump()
        elif self.game.inputs['released'].get('v'):
            self.jump_release()

        if self.game.inputs['held'].get('d'):
            self.vel[0] += 0.3
        elif self.game.inputs['held'].get('a'):
            self.vel[0] -= 0.3

        self.vel[0] = max(-3, min(3, self.vel[0]))

        super().update(rects)



class Player2(Player):
    pass
