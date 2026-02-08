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
        surf = pygame.Surface((car.length,car.witdh), pygame.SRCALPHA)
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
            car.angle - math.pi / 4,
            car.angle + math.pi / 2,
            car.angle - math.pi / 2
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

    def render(self, car=None, cars=None, draw_sensors=True):
        """
        Render the scene.
        
        Args:
            car: Single car to render (for backward compatibility)
            cars: List of cars to render
            draw_sensors: Whether to draw sensor rays
        """
        self.clock.tick(self.fps)

        self.screen.fill((30, 30, 30))
        self.draw_world()

        # Handle single car (backward compatibility)
        if car:
            self.draw_car(car)
            if draw_sensors:
                self.draw_sensors(car)
        
        # Handle multiple cars
        if cars:
            colors = [
                (230, 50, 50),   # Red
                (50, 230, 50),   # Green
                (50, 50, 230),   # Blue
                (230, 230, 50),  # Yellow
                (230, 50, 230),  # Magenta
                (50, 230, 230),  # Cyan
            ]
            
            for i, car_obj in enumerate(cars):
                color = colors[i % len(colors)]
                self.draw_car_colored(car_obj, color)
                if draw_sensors and i == 0:  # Only draw sensors for first car
                    self.draw_sensors(car_obj)

        pygame.display.flip()
    
    def draw_car_colored(self, car, color):
        """Draw a car with a specific color."""
        surf = pygame.Surface((car.length, car.witdh), pygame.SRCALPHA)
        surf.fill(color)

        rotated = pygame.transform.rotate(
            surf, -math.degrees(car.angle)
        )

        rect = rotated.get_rect(center=(car.x, car.y))
        self.screen.blit(rotated, rect)

