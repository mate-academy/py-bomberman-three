import random

import pygame
import abc

from app.config import DEFAULT_ENEMY_TIMEOUT, DEFAULT_EFFECT_TIMEOUT
from sprites import Spider, Bird, Boar, Healing, Slow, Fast

from mixins import EngineMixin


class Event(EngineMixin, abc.ABC):
    def __init__(self, ms_timeout):
        super().__init__()
        self.ms_timeout = ms_timeout

    @abc.abstractmethod
    def action(self):
        pass


class AddEnemy(Event):
    def __init__(self, ms_timeout=DEFAULT_ENEMY_TIMEOUT):
        super().__init__(ms_timeout)

        self.event_no = pygame.USEREVENT + 1
        pygame.USEREVENT = self.event_no
        pygame.time.set_timer(self.event_no, self.ms_timeout)
        self.engine.add_event(self)

    def action(self):
        self.choice_enemy()

    @staticmethod
    def choice_enemy():
        chance = random.randint(1, 10)
        common_enemy = "Spider()"
        advanced_enemies = ["Bird()", "Boar()"]
        if chance >= 8:
            return eval(random.choice(advanced_enemies))
        else:
            return eval(common_enemy)


class AddEffect(Event):
    def __init__(self, ms_timeout=DEFAULT_EFFECT_TIMEOUT):
        super().__init__(ms_timeout)

        self.event_no = pygame.USEREVENT + 2
        pygame.USEREVENT = self.event_no
        pygame.time.set_timer(self.event_no, self.ms_timeout)
        self.engine.add_event(self)

    def action(self):
        self.choice_effect()

    @staticmethod
    def choice_effect():
        all_effects = ["Healing()", "Slow()", "Fast()"]
        return eval(random.choice(all_effects))
