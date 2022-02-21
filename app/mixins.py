import pygame

from engine import Engine


class EngineMixin:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.engine = Engine()


class MovingMixin:
    def move_collision_out(self, x_speed, y_speed):
        is_on_bomb = self.is_on_bomb if hasattr(self, "is_on_bomb") else False
        is_on_rock = self.is_on_bomb if hasattr(self, "is_on_rock") else False
        wall_collision = pygame.sprite.spritecollideany(
            self, self.engine.groups["walls"]
        )
        bomb_collision = pygame.sprite.spritecollideany(
            self, self.engine.groups["bombs"]
        )
        rock_collision = pygame.sprite.spritecollideany(
            self, self.engine.groups["rocks"]
        )
        if (wall_collision
                or bomb_collision
                or rock_collision
                and not is_on_bomb
                and not is_on_rock):
            self.rect.move_ip(-x_speed, -y_speed)


class FlyingMixin:
    def move_collision_out(self, x_speed, y_speed):
        is_on_bomb = self.is_on_bomb if hasattr(self, "is_on_bomb") else False
        if pygame.sprite.spritecollideany(
            self, self.engine.groups["bombs"]
        ) and not is_on_bomb:
            self.rect.move_ip(-x_speed, -y_speed)
