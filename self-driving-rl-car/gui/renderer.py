import pygame
import math

class Renderer:
    def __init__(self, image_path, width=800, height=600, fps=60):
        pygame.init()

        self.fps = fps

        # Screen
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        # World image
        self.map_img = pygame.image.load(image_path).convert()
        w, h = self.map_img.get_size()
        
    def draw_world(self):
        self.screen.blit(self.map_img, (0, 0))

    def draw_car(self, car):
        surf = pygame.Surface((30, 20), pygame.SRCALPHA)
        surf.fill((230, 50, 50))

        rotated = pygame.transform.rotate(
            surf, -math.degrees(car.angle)
        )

        rect = rotated.get_rect(center=(car.x, car.y))
        self.screen.blit(rotated, rect)

    def draw_sensors(self, car):
        angles = [
            car.angle,
            car.angle + math.pi / 4,
            car.angle - math.pi / 4
        ]

        distances = car.sensors()

        for angle, dist in zip(angles, distances):
            end_x = int(car.x + math.cos(angle) * dist)
            end_y = int(car.y + math.sin(angle) * dist)

            pygame.draw.line(
                self.screen,
                (255, 0, 0),
                (int(car.x), int(car.y)),
                (end_x, end_y),
                2
            )


    # ---------- MAIN RENDER ----------

    def render(self, car=None, draw_sensors=True):
        self.clock.tick(self.fps)

        self.screen.fill((30, 30, 30))
        self.draw_world()

        if car:
            self.draw_car(car)
            if draw_sensors:
                self.draw_sensors(car)

        pygame.display.flip()
