import math
import pygame
from pygame.math import Vector2
from simulation.world import CollisionMap


class Car:
    def __init__(self,map, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.speed = 0.0

        self.map = map

        self.max_speed = 5.0
        self.vertical_acc = 0.2
        self.angular_acc = 0.2

    def step(self, dikey, acisal):
        """
        throttle ∈ [-1, 1]
        steer    ∈ [-1, 1]
        """

        self.speed += dikey * self.vertical_acc
        self.speed = max(-self.max_speed, min(self.max_speed, self.speed))

        self.angle += acisal / math.pi

        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def sensors(self):
        angles = [
            self.angle,                
            self.angle + math.pi / 4,
            self.angle - math.pi / 4,
        ]

        distances = []

        for a in angles:
            d = self.map.cast_ray(self.x, self.y, a)
            distances.append(d)

        return distances  

        

        
    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "sin": math.sin(self.angle),
            "cos": math.cos(self.angle),
            "speed": self.speed
        }