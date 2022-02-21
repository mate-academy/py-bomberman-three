import random

import pygame

from abc import ABC, abstractmethod
from app.config import DEFAULT_SCORE_INCREASE, SCREEN_WIDTH, SCREEN_HEIGHT, BOMB_COOLDOWN
from app.sprites import CollisionMixin, EngineSprite, Rock, Bomb, SlowEffect, try_drop_effect, FastEffect


class Enemy(ABC, EngineSprite, CollisionMixin):
    def __init__(self):
        super(Enemy, self).__init__()
        self.engine.add_to_group(self, 'enemies')
        self.engine.add_to_group(self, '__flammable')

    @abstractmethod
    def moving(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def kill(self) -> None:
        super().kill()


class Spider(Enemy):
    def __init__(self, initial_position):
        super(Enemy, self).__init__()
        self.engine.add_to_group(self, 'enemies')
        self.engine.add_to_group(self, '__flammable')
        self.speed = 3
        self.image_front = pygame.image.load(
            "images/spider_front.png"
        ).convert_alpha()
        self.image_back = pygame.image.load(
            "images/spider_back.png"
        ).convert_alpha()
        self.image_left = pygame.image.load(
            "images/spider_left.png"
        ).convert_alpha()
        self.image_right = pygame.image.load(
            "images/spider_right.png"
        ).convert_alpha()
        self.surf = self.image_front
        self.rect = self.surf.get_rect(center=initial_position)
        self.player = self.engine.groups['player'].sprites()[0]
        self.possible_effect = FastEffect

    def moving(self):
        player = self.engine.groups["player"].sprites()[0]
        x_diff = self.rect.centerx - player.rect.centerx
        y_diff = self.rect.centery - player.rect.centery

        if not y_diff:
            pass
        elif y_diff < 0:
            self.surf = self.image_front
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
        else:
            self.surf = self.image_back
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
        if not x_diff:
            pass
        elif x_diff < 0:
            self.surf = self.image_right
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)
        else:
            self.surf = self.image_left
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)

    def update(self):
        self.moving()

    def kill(self) -> None:
        self.engine.scoreboard.score += DEFAULT_SCORE_INCREASE
        try_drop_effect(self.possible_effect, self.rect.center)
        super().kill()


class Boar(Enemy):
    def __init__(self, initial_position):
        super().__init__()
        self.engine.add_to_group(self, 'enemies')
        self.engine.add_to_group(self, '__flammable')
        self.speed = 2
        self.image_front = pygame.image.load(
            "images/boar_front.png"
        ).convert_alpha()
        self.image_back = pygame.image.load(
            "images/boar_back.png"
        ).convert_alpha()
        self.image_left = pygame.image.load(
            "images/boar_left.png"
        ).convert_alpha()
        self.image_right = pygame.image.load(
            "images/boar_right.png"
        ).convert_alpha()
        self.surf = self.image_front
        self.rect = self.surf.get_rect(center=initial_position)
        self.player = self.engine.groups['player'].sprites()[0]
        self.time_to_place_rock = 120
        self.is_on_rock = False

    def moving(self):
        player = self.engine.groups["player"].sprites()[0]
        x_diff = self.rect.centerx - player.rect.centerx
        y_diff = self.rect.centery - player.rect.centery

        if not y_diff:
            pass
        elif y_diff < 0:
            self.surf = self.image_front
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
        else:
            self.surf = self.image_back
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
        if not x_diff:
            pass
        elif x_diff < 0:
            self.surf = self.image_right
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)
        else:
            self.surf = self.image_left
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)

    def place_rock(self):
        self.time_to_place_rock -= 1
        if self.time_to_place_rock < 1:
            self.is_on_rock = True
            Rock(self.rect.center)
            self.time_to_place_rock = 120
        if not pygame.sprite.spritecollideany(
                self, self.engine.groups["rocks"]
        ):
            self.is_on_rock = False

    def update(self):
        self.moving()
        self.place_rock()

    def kill(self) -> None:
        self.engine.scoreboard.score += int(DEFAULT_SCORE_INCREASE * 1.5)
        super().kill()


class Bird(Enemy):
    def __init__(self, initial_position):
        super(Enemy, self).__init__()
        self.engine.add_to_group(self, 'enemies')
        self.engine.add_to_group(self, '__flammable')
        self.speed = 1
        self.image_left = pygame.image.load(
            "images/bird_left.png"
        ).convert_alpha()
        self.image_right = pygame.image.load(
            "images/bird_right.png"
        ).convert_alpha()
        self.surf = self.image_left
        self.rect = self.surf.get_rect(center=initial_position)
        self.time_to_drop_bomb = BOMB_COOLDOWN * 10
        self.new_location = self.get_new_location()
        self.possible_effect = SlowEffect

    def moving(self):
        x_diff = self.rect.centerx - self.new_location[0]
        y_diff = self.rect.centery - self.new_location[1]

        if not y_diff:
            pass
        elif y_diff < 0:
            self.rect.move_ip(0, self.speed)
        else:
            self.rect.move_ip(0, -self.speed)
        if not x_diff:
            pass
        elif x_diff < 0:
            self.surf = self.image_right
            self.rect.move_ip(self.speed, 0)
        else:
            self.surf = self.image_left
            self.rect.move_ip(-self.speed, 0)

    @staticmethod
    def get_new_location():
        return (
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )

    def update(self):
        self.moving()
        self.time_to_drop_bomb -= 1
        if self.rect.center == self.new_location:
            self.new_location = self.get_new_location()
        if not self.time_to_drop_bomb:
            self.drop_bomb()

    def drop_bomb(self):
        Bomb(self.rect.center)
        self.time_to_drop_bomb = BOMB_COOLDOWN * 10

    def kill(self) -> None:
        self.engine.scoreboard.score += DEFAULT_SCORE_INCREASE * 2
        try_drop_effect(self.possible_effect, self.rect.center)
        super().kill()
