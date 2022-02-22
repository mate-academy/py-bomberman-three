import pygame

from sprites import Player, Wall
from event import AddSpider, AddBoar, AddBird
from engine import Engine
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DEFAULT_OBJ_SIZE,
    FRAMES_PER_SECOND,
    BACKGROUND_COLOR
)


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

engine = Engine(screen=screen, clock=clock)

player = Player()

Wall.generate_walls((SCREEN_WIDTH, SCREEN_HEIGHT),
                    (DEFAULT_OBJ_SIZE, DEFAULT_OBJ_SIZE))

add_spider = AddSpider(1000)
add_boar = AddBoar(3000)
add_bird = AddBird(5000)
engine.add_event(add_spider)
engine.add_event(add_boar)
engine.add_event(add_bird)

engine.running = True

while engine.running:
    engine.events_handling()

    # Update all groups
    engine.groups_update()

    engine.screen.fill(BACKGROUND_COLOR)

    # Draw all sprites
    engine.draw_all_sprites()

    engine.draw_interface()

    pygame.display.flip()
    engine.clock.tick(FRAMES_PER_SECOND)

pygame.quit()
