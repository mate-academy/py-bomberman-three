import pygame
import random

from collections import defaultdict

from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from app.config import (
    ADDENEMY, SCREEN_WIDTH, SCREEN_HEIGHT,
    DEFAULT_OBJ_SIZE, DEFAULT_EVENT_TIMEOUT
)


def singleton(class_):
    _instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in _instances:
            _instances[class_] = class_(*args, **kwargs)
        return _instances[class_]

    return get_instance


@singleton
class Engine:
    def __init__(self, screen, clock):
        self.running = True
        self.screen = screen
        self.clock = clock
        self.spawner = Spawner()

        self.groups = defaultdict(pygame.sprite.Group)
        self.all_sprites = pygame.sprite.Group()
        self.scoreboard = Scoreboard()

    def events_handling(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
            if event.type == ADDENEMY:
                self.spawner.spawn_enemy()

            # Did user click quit button?
            elif event.type == QUIT:
                self.running = False

    def add_to_group(self, sprite, group):
        self.groups[group].add(sprite)
        self.all_sprites.add(sprite)

    def groups_update(self):
        groups = (
            [group for name, group in list(self.groups.items())
             if not name.startswith('__')]
        )
        for group in groups:
            group.update()

    def draw_all_sprites(self):
        for sprite in self.all_sprites:
            self.screen.blit(sprite.surf, sprite.rect)


class Spawner:
    def __init__(self):
        super(Spawner, self).__init__()
        pygame.time.set_timer(ADDENEMY, DEFAULT_EVENT_TIMEOUT)
        self.enemy_pull = {}

    @staticmethod
    def get_random_position():
        side = random.randint(0, 1)
        if side:
            x = random.randrange(0, SCREEN_WIDTH, DEFAULT_OBJ_SIZE) // 2
            y = random.choice([0, SCREEN_HEIGHT])
        else:
            x = random.choice([0, SCREEN_WIDTH])
            y = random.randrange(0, SCREEN_HEIGHT, DEFAULT_OBJ_SIZE) // 2
        return x, y

    def add_enemy_with_spawn_chance_to_pull(self, enemy, chance):
        self.enemy_pull[chance] = enemy

    def spawn_enemy(self):
        random_coordinates = self.get_random_position()
        enemy = random.choices(
            list(self.enemy_pull.values()),
            weights=list(self.enemy_pull.keys())
        )[0]
        enemy(random_coordinates)


class Scoreboard:
    def __init__(self):
        self.score = 0

    def draw_interface(self, engine):
        font = pygame.font.SysFont("comicsans", 15, True)
        text_score = font.render("Score: " + str(self.score), True, (255, 255, 255))
        engine.screen.blit(text_score, (10, 10))

        player = engine.groups["player"].sprites()[0]
        text_health = font.render("Health: " + str(player.get_health()),
                                  True, (0, 255, 0))
        text_speed = font.render("Speed: " + str(player.get_speed()),
                                 True, (0, 255, 0))

        engine.screen.blit(text_health,
                           (SCREEN_WIDTH - text_health.get_width() - 10, 10))
        engine.screen.blit(text_speed,
                           (SCREEN_WIDTH - text_speed.get_width() - 10, 30))
