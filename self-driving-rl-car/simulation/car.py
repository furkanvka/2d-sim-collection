import math
import pygame
from pygame.math import Vector2
from simulation.world import CollisionMap


class Car:
    def __init__(self,map,angle=0, x=0.0, y=0.0,length = 30,witdh =20):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0.0


        self.length = length
        self.witdh = witdh

        self.map = map


        self.friction = 0.05 
        self.max_speed = 5.0
        self.vertical_acc = 0.2
        self.angular_acc = 0.2

        self.angular_speed = 0.0
        self.max_angular_speed = math.radians(6)   # ≈ 0.105 rad
        self.angular_acc = math.radians(1.0)        # ≈ 0.017 rad
        self.angular_friction = 0.25

    def step(self, dikey, acisal):
        old_x = self.x
        old_y = self.y
        old_angle = self.angle

        # 🚗 Gaz / fren
        self.speed += dikey * self.vertical_acc
        self.speed = max(0, min(self.max_speed, self.speed))

        if abs(dikey) < 1e-3:
            self.speed *= (1 - self.friction)

        if abs(self.speed) < 0.01:
            self.speed = 0.0

        # 🔄 Açısal hareket (π ile oranlama + min/max)
        self.angular_speed += (acisal * self.angular_acc) / (2 * math.pi)

        self.angular_speed = max(
            -self.max_angular_speed,
            min(self.max_angular_speed, self.angular_speed)
        )

        if abs(acisal) < 1e-3:
            self.angular_speed *= (1 - self.angular_friction)

        if abs(self.angular_speed) < 0.001:
            self.angular_speed = 0.0

        self.angle += self.angular_speed

        self.angle += self.angular_speed

        # 📍 Pozisyon güncelle
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

        # 🧱 Çarpışma kontrolü
        if self.isitinwall():
            self.x = old_x
            self.y = old_y
            self.angle = old_angle
            self.speed = 0.0
            self.angular_speed = 0.0
            return False

        return True



    def sensors(self):
        angles = [
            self.angle,                
            self.angle + math.pi / 4,
            self.angle - math.pi / 4,
            self.angle + math.pi / 2,
            self.angle - math.pi / 2
        ]

        distances = []

        for a in angles:
            d = self.map.cast_ray(self.x, self.y, a)
            distances.append(d)

        return distances 


    def isitinwall(self):
        half_l = self.length / 2
        half_w = self.witdh / 2

        forward = Vector2(math.cos(self.angle), math.sin(self.angle))
        right   = Vector2(-math.sin(self.angle), math.cos(self.angle))

        corners = [
            Vector2(self.x, self.y) + forward * half_l + right * half_w,
            Vector2(self.x, self.y) + forward * half_l - right * half_w,
            Vector2(self.x, self.y) - forward * half_l + right * half_w,
            Vector2(self.x, self.y) - forward * half_l - right * half_w,
        ]

        for c in corners:
            if self.map.is_wall(c.x, c.y):
                return True

        return False

        
    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "sin": math.sin(self.angle),
            "cos": math.cos(self.angle),
            "speed": self.speed
        }
    
    def reset(self,angle = (math.pi/2), x=150, y=150):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0.0
        self.angular_speed = 0.0