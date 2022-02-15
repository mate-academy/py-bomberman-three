import pygame

from collections import defaultdict

from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Engine(metaclass=SingletonMeta):
    def __init__(self, screen, clock):
        self.running = True
        self.screen = screen
        self.clock = clock

        self.groups = defaultdict(pygame.sprite.Group)
        self.all_sprites = pygame.sprite.Group()
        self.events = dict()

    def add_event(self, event):
        self.events[event.event_no] = event

    def events_handling(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False

            # Did user click quit button?
            elif event.type == QUIT:
                self.running = False

            elif event.type in self.events:
                self.events[event.type].action()

    def add_to_group(self, sprite, group):
        self.groups[group].add(sprite)
        self.all_sprites.add(sprite)

    def groups_update(self):
        groups = [entity for entity in self.groups.values()]
        for group in groups:
            group.update()

    def draw_all_sprites(self):
        for sprite in self.all_sprites:
            self.screen.blit(sprite.surf, sprite.rect)
