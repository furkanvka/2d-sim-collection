from PIL import Image
import numpy as np
import math

class CollisionMap:
    def __init__(self, image_path):
        img = Image.open(image_path).convert("L")
        self.map = np.array(img)

    def is_wall(self, x, y):
        if x < 0 or y < 0 or y >= self.map.shape[0] or x >= self.map.shape[1]:
            return True
        return self.map[y, x] < 128

    def cast_ray(self,x, y, angle, max_length=30, step=1):

        dx = math.cos(angle)
        dy = math.sin(angle)

        distance = 0

        while distance < max_length:
            rx = int(x + dx * distance)
            ry = int(y + dy * distance)

            if self.is_wall(rx, ry):
                return distance

            distance += step

        return max_length
