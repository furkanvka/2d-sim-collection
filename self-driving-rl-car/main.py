import pygame

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
    car = Car(map,150, 150)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        throttle = 0.0
        steer = 0.0

        car.step(throttle, steer)

        renderer.render(car)

    pygame.quit()


if __name__ == "__main__":
    main()
