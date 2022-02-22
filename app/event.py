import pygame
import abc

from sprites import Spider, Boar, Bird

from mixins import EngineMixin


class Event(EngineMixin, abc.ABC):
    def __init__(self, ms_timeout=1000):
        super().__init__()
        self.ms_timeout = ms_timeout

        self.event_no = pygame.USEREVENT + 1
        pygame.USEREVENT = self.event_no
        pygame.time.set_timer(self.event_no, self.ms_timeout)
        self.engine.add_event(self)

    @abc.abstractmethod
    def action(self):
        pass


class AddSpider(Event):

    def action(self):
        Spider()


class AddBoar(Event):
    def action(self):
        Boar()


class AddBird(Event):
    def action(self):
        Bird()
