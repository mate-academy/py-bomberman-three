import random
import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE
from abc import ABC, abstractmethod

from mixins import MovingMixin, EngineMixin, FlyingMixin
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DEFAULT_OBJ_SIZE,
    DEFAULT_PLAYER_HP,
    DEFAULT_PLAYER_SPEED,
    BOMB_TIMER,
    PLANT_BOMB_COOLDOWN,
    BOMB_EXPLODE_RANGE,
    FIRE_LIFETIME,
    BoarConstants,
    BirdConstants,
    SpiderConstants,
    ROCK_SPAWN_COOLDOWN,
    HEALING_EFFECT,
    SLOW_EFFECT,
    ACCELERATE_EFFECT,
)


class EngineSprite(EngineMixin, pygame.sprite.Sprite):
    pass


class EngineMovingSprite(MovingMixin, EngineSprite):
    pass


class Player(EngineMovingSprite):
    def __init__(self):
        super(Player, self).__init__()
        self.engine.add_to_group(self, "player")
        self.engine.add_to_group(self, "flammable")
        self.surf = pygame.image.load(
            "images/player_front.png"
        ).convert_alpha()
        self.rect = self.surf.get_rect()
        self.plant_bomb_cooldown = 0
        self.is_on_bomb = False
        self.health = DEFAULT_PLAYER_HP
        self.speed = DEFAULT_PLAYER_SPEED

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if self.health <= 0:
            self.kill()

        if self.plant_bomb_cooldown:
            self.plant_bomb_cooldown -= 1

        if not pygame.sprite.spritecollideany(
                self,
                self.engine.groups["bombs"]
        ):
            self.is_on_bomb = False

        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
            self.surf = pygame.image.load(
                "images/player_back.png"
            ).convert_alpha()

        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
            self.surf = pygame.image.load(
                "images/player_front.png"
            ).convert_alpha()

        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)
            self.surf = pygame.image.load(
                "images/player_left.png"
            ).convert_alpha()

        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)
            self.surf = pygame.image.load(
                "images/player_right.png"
            ).convert_alpha()

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        if pressed_keys[K_SPACE]:
            self.place_bomb()

    def place_bomb(self):
        if not self.plant_bomb_cooldown:
            self.is_on_bomb = True
            Bomb(self.rect.center)
            self.plant_bomb_cooldown = PLANT_BOMB_COOLDOWN

    def change_health(self, hp: int):
        self.health += hp

    def get_health(self):
        return self.health

    def get_speed(self):
        return self.speed

    def kill(self) -> None:
        super().kill()
        self.engine.running = False


class Wall(EngineSprite):
    def __init__(self, center_pos: tuple):
        super().__init__()
        self.engine.add_to_group(self, "walls")
        self.surf = pygame.image.load("images/wall.png").convert_alpha()
        self.rect = self.surf.get_rect(center=center_pos)

    @classmethod
    def generate_walls(cls, field_size: tuple, wall_size: tuple):
        walls_centers = cls.create_centers_of_walls(field_size, wall_size)
        for obs_center in walls_centers:
            Wall(obs_center)

    @staticmethod
    def create_centers_of_walls(field_size: tuple, wall_size: tuple):
        center_width = wall_size[0] + wall_size[0] // 2
        center_height = wall_size[1] + wall_size[1] // 2
        centers = []

        while center_height < field_size[1] - wall_size[1]:
            while center_width < field_size[0] - wall_size[0]:
                centers.append((center_width, center_height))
                center_width += 2 * wall_size[0]
            center_height += 2 * wall_size[1]
            center_width = wall_size[0] + wall_size[0] // 2

        return centers


class Droppable(EngineSprite, ABC):
    def __init__(
            self,
            group_name: str,
            group_image: str,
            owner_center,
    ):
        super().__init__()
        self.engine.add_to_group(self, group_name)
        self.surf = pygame.image.load(group_image).convert_alpha()
        self.rect = self.surf.get_rect(
            center=self.get_self_center(owner_center)
        )

    def get_self_center(self, owner_center):
        lines = self.get_line_obj_placed(owner_center)
        return (
            lines[0] * DEFAULT_OBJ_SIZE + self.surf.get_width() // 2,
            lines[1] * DEFAULT_OBJ_SIZE + self.surf.get_height() // 2,
        )

    @staticmethod
    def get_line_obj_placed(owner_center):
        width = owner_center[0] // DEFAULT_OBJ_SIZE
        height = owner_center[1] // DEFAULT_OBJ_SIZE
        return width, height

    @abstractmethod
    def update(self):
        raise NotImplementedError

    @classmethod
    def generate_instance(cls, owner_center):
        return cls(owner_center=owner_center)


class Heal(Droppable):
    def __init__(self, owner_center):
        super().__init__(
            group_name='heal',
            group_image='images/healing_effect.png',
            owner_center=owner_center
        )
        self.heal = HEALING_EFFECT

    def update(self):
        if pygame.sprite.spritecollideany(
            self, self.engine.groups['player']
        ):
            for player in self.engine.groups['player']:
                player.health += self.heal
            self.kill()


class Slow(Droppable):
    def __init__(self, owner_center):
        super().__init__(
            group_name='slow',
            group_image='images/slow_effect.png',
            owner_center=owner_center
        )
        self.slow = SLOW_EFFECT

    def update(self):
        if pygame.sprite.spritecollideany(
            self, self.engine.groups['player']
        ):
            for player in self.engine.groups['player']:
                player.speed -= self.slow
                if player.speed <= 0:
                    player.speed = 1
            self.kill()


class Accelerate(Droppable):
    def __init__(self, owner_center):
        super().__init__(
            group_name='heal',
            group_image='images/healing_effect.png',
            owner_center=owner_center
        )
        self.accelerate = ACCELERATE_EFFECT

    def update(self):
        if pygame.sprite.spritecollideany(
            self, self.engine.groups['player']
        ):
            for player in self.engine.groups['player']:
                player.speed += self.accelerate
            self.kill()


class Bomb(Droppable):
    def __init__(self, owner_center):
        super().__init__(
            group_image='images/bomb.png',
            group_name='bombs',
            owner_center=owner_center,
        )
        self.lifetime = BOMB_TIMER
        self.explode_range = BOMB_EXPLODE_RANGE

    def update(self):
        self.lifetime -= 1
        if not self.lifetime:
            self.explode()

    def explode(self):
        fires = [(self.rect.centerx, self.rect.centery)]

        width = self.rect.centerx
        for it in range(1, self.explode_range + 1):
            height = self.rect.centery + it * DEFAULT_OBJ_SIZE
            if self.walls_collide_point((width, height)):
                break
            Fire((width, height))

            height = self.rect.centery - it * DEFAULT_OBJ_SIZE
            if self.walls_collide_point((width, height)):
                break
            Fire((width, height))

        height = self.rect.centery
        for it in range(1, self.explode_range + 1):
            width = self.rect.centerx + it * DEFAULT_OBJ_SIZE
            if self.walls_collide_point((width, height)):
                break
            Fire((width, height))

            width = self.rect.centerx - it * DEFAULT_OBJ_SIZE
            if self.walls_collide_point((width, height)):
                break
            Fire((width, height))

        for item in fires:
            Fire(item)
        self.kill()

    def walls_collide_point(self, point):
        for sprite in self.engine.groups["walls"].sprites():
            if sprite.rect.collidepoint(point):
                return True
        return False


class Rock(Droppable):
    def __init__(self, owner_center):
        super().__init__(
            group_name='rocks',
            group_image='images/rock.png',
            owner_center=owner_center,
        )

    def update(self):
        if pygame.sprite.spritecollideany(
                self,
                self.engine.groups['fires'],
        ):
            self.kill()


class Fire(EngineSprite):
    def __init__(self, center_pos: tuple):
        super().__init__()
        self.engine.add_to_group(self, "fires")
        self.width = DEFAULT_OBJ_SIZE
        self.height = DEFAULT_OBJ_SIZE
        self.surf = pygame.image.load("images/explosion_1.png").convert_alpha()
        self.rect = self.surf.get_rect(center=(center_pos[0], center_pos[1]))
        self.lifetime = FIRE_LIFETIME

    def update(self):
        self.lifetime -= 1

        if self.lifetime < 0:
            self.kill()
        elif self.lifetime < 3:
            self.surf = pygame.image.load(
                "images/explosion_3.png"
            ).convert_alpha()
        elif self.lifetime < 6:
            self.surf = pygame.image.load(
                "images/explosion_2.png"
            ).convert_alpha()

        # kill all flammable units that touch the fire
        flamed = pygame.sprite.spritecollideany(
            self, self.engine.groups["flammable"]
        )
        if flamed:
            flamed.kill()


class BaseEnemy(EngineMovingSprite, ABC):
    def __init__(
            self,
            group_name: str,
            group_speed: int,
            group_images: dict,
            group_score: int,
            group_damage: int,
    ):
        super().__init__()
        self.engine.add_to_group(self, group_name)
        self.engine.add_to_group(self, "flammable")
        self.speed = group_speed
        self.image_front = pygame.image.load(
            group_images['front']
        ).convert_alpha()
        self.image_back = pygame.image.load(
            group_images['back']
        ).convert_alpha()
        self.image_left = pygame.image.load(
            group_images['left']
        ).convert_alpha()
        self.image_right = pygame.image.load(
            group_images['right']
        ).convert_alpha()
        self.surf = self.image_front
        self.position = self.generate_position()
        self.rect = self.surf.get_rect(center=self.position[:2])
        self.score_points = group_score
        self.damage = group_damage

    @staticmethod
    def generate_position() -> tuple:
        delta = 50
        direction = random.choice(["left", "top", "right", "bottom"])
        if direction == "left":
            width = -delta
            height = random.randint(0, SCREEN_HEIGHT)

        if direction == "top":
            width = random.randint(0, SCREEN_WIDTH)
            height = -delta

        if direction == "right":
            width = SCREEN_WIDTH + delta
            height = random.randint(0, SCREEN_HEIGHT)

        if direction == "bottom":
            width = random.randint(0, SCREEN_WIDTH)
            height = SCREEN_HEIGHT + delta

        return width, height, direction

    @abstractmethod
    def move(self):
        raise NotImplementedError

    @abstractmethod
    def constant_changes(self):
        raise NotImplementedError

    @abstractmethod
    def additional_action(self):
        raise NotImplementedError

    def kill(self) -> None:
        super().kill()
        effects = [Heal, Slow, Accelerate]
        random.choice(effects).generate_instance(self.rect.center)
        self.engine.score += self.score_points

    def collisions_handling(self):
        player = self.engine.groups["player"].sprites()[0]
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            player.change_health(-self.damage)
            self.kill()

    def update(self):
        self.constant_changes()

        self.collisions_handling()
        self.move()
        self.additional_action()

    @classmethod
    def generate_instance(cls):
        return cls()


class BirdEnemy(FlyingMixin, BaseEnemy):
    def __init__(self):
        super().__init__(
            group_name=BirdConstants.group_name,
            group_speed=BirdConstants.group_speed,
            group_images=BirdConstants.group_images,
            group_score=BirdConstants.group_score,
            group_damage=BirdConstants.group_damage,
        )

        self.plant_bomb_cooldown = PLANT_BOMB_COOLDOWN
        self.is_on_bomb = False

    def move(self):
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

    def constant_changes(self):
        self.plant_bomb_cooldown -= 1

    def plant_bomb(self):
        Bomb(self.rect.center)
        self.is_on_bomb = True

    def additional_action(self):
        if not self.plant_bomb_cooldown:
            self.plant_bomb_cooldown = PLANT_BOMB_COOLDOWN
            self.plant_bomb()
        if not pygame.sprite.spritecollideany(
            self, self.engine.groups['bombs']
        ):
            self.is_on_bomb = False


class BoarEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(
            group_name=BoarConstants.group_name,
            group_speed=BoarConstants.group_speed,
            group_images=BoarConstants.group_images,
            group_score=BoarConstants.group_score,
            group_damage=BoarConstants.group_damage,
        )
        self.rock_cooldown = ROCK_SPAWN_COOLDOWN

    def constant_changes(self):
        self.rock_cooldown -= 1

    def additional_action(self):
        if not self.rock_cooldown:
            self.rock_cooldown = ROCK_SPAWN_COOLDOWN
            Rock(self.rect.center)

    def move(self):
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


class SpiderEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(
            group_name=SpiderConstants.group_name,
            group_speed=SpiderConstants.group_speed,
            group_images=SpiderConstants.group_images,
            group_score=SpiderConstants.group_score,
            group_damage=SpiderConstants.group_damage,
        )

    def move(self):
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

    def additional_action(self):
        pass

    def constant_changes(self):
        pass
