from .entity import PhysicsEntity

class Player(PhysicsEntity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
