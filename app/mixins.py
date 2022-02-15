import pygame

from engine import Engine


class EngineMixin:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.engine = Engine()


class MovingMixin:
    def move_collision_out(self, x_speed, y_speed):
        on_bomb = self.on_bomb if hasattr(self, "on_bomb") else False
        if (
            pygame.sprite.spritecollideany(self, self.engine.groups["walls"])
            or pygame.sprite.spritecollideany(self, self.engine.groups["bombs"])
            and not on_bomb
        ):
            self.rect.move_ip(-x_speed, -y_speed)
