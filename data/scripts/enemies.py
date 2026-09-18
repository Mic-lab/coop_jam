from .entity import PhysicsEntity

class Enemy(PhysicsEntity):

    SPEED = 2
    ACCELERATION = 0.1

    def __init__(self, game, *args, **kwargs):
        self.game = game
        super().__init__(*args, **kwargs)

    def update(self, rects=None):
        player_1 = self.game.game_map.level.player_1
        player_2 = self.game.game_map.level.player_2

        accel = (player_1.pos - self.pos)
        if accel.length() > self.ACCELERATION:
            accel.scale_to_length(self.ACCELERATION)
        self.vel += accel
        if self.vel.length() > self.SPEED:
            self.vel.scale_to_length(self.SPEED)

        return super().update(rects)
