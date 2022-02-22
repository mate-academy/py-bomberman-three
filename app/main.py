import pygame

from sprites import Player, Wall, Spider, Boar, Bird
from event import AddEnemy
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

add_enemy_spider = AddEnemy(1000, Spider)
engine.add_event(add_enemy_spider)
add_enemy_boar = AddEnemy(3000, Boar)
engine.add_event(add_enemy_boar)
add_enemy_bird = AddEnemy(1000, Bird)
engine.add_event(add_enemy_bird)


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
