import pygame
from .entity import Entity

class Orb(Entity):

    def __init__(self, pos):
        super().__init__(pos, 'orb', action='idle', collision_mode='soft_tracked')
        self.tag = 'orb'
