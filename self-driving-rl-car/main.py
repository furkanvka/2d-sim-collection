import pygame
import math

from simulation.car import Car
from simulation.world import CollisionMap
from gui.renderer import Renderer


WIDTH, HEIGHT = 800, 600
MAP_PATH = "map.png"

def main():
    pygame.init()

    renderer = Renderer(
        image_path=MAP_PATH,
        width=WIDTH,
        height=HEIGHT,
        fps=60
    )

    map = CollisionMap(MAP_PATH)
    car = Car(map,(math.pi / 2), 120 , 120)

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ⌨️ Klavye okuma
        keys = pygame.key.get_pressed()

        throttle = 0.0
        steer = 0.0

        if keys[pygame.K_w]:
            throttle = 1.0
        if keys[pygame.K_s]:
            throttle = -1.0

        if keys[pygame.K_a]:
            steer = -1.0
        if keys[pygame.K_d]:
            steer = 1.0

        if not car.step(throttle, steer):
            car.reset(math.pi / 2,120,120)


        
        renderer.render(car)

    pygame.quit()

if __name__ == "__main__":
    main()
