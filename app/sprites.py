import random
from abc import ABC, abstractmethod

import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from mixins import MovingMixin, EngineMixin
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
    PLANT_BOMB_COOLDOWN_BIRD,
    PLANT_ROCK_COOLDOWN_BOAR,
    DEFAULT_ENEMY_SPEED,
    DEFAULT_SCORE_POINT, TIMER_EFFECT
)


class EngineSprite(EngineMixin, pygame.sprite.Sprite):
    pass


class EngineMovingSprite(MovingMixin, EngineSprite):
    pass


class Enemy(ABC, EngineMovingSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "enemies")
        self.engine.add_to_group(self, "__flammable")
        self.speed = DEFAULT_ENEMY_SPEED
        self.score_points = DEFAULT_SCORE_POINT

    def update(self):
        self.collisions_handling()
        self.move()

    @abstractmethod
    def move(self):
        pass

    def collisions_handling(self):
        player = self.engine.player
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            player.change_health(-10)
            self.kill()

    @staticmethod
    def generate_position() -> tuple:
        delta = 50
        direction = random.choice(["left", "top", "right", "bottom"])
        width = 0
        height = 0
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

    def kill(self) -> None:
        super().kill()
        self.engine.score += self.score_points


class Effect(ABC, EngineMovingSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "__flammable")
        self.engine.add_to_group(self, "effects")
        self.time_life = TIMER_EFFECT

    def update(self):
        self.collisions_handling()
        self.is_life()
        self.set_effect()

    @abstractmethod
    def set_effect(self):
        pass

    def collisions_handling(self):
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            self.kill()

    def kill(self) -> None:
        super().kill()

    def is_life(self):
        if self.time_life:
            self.time_life -= 1
        else:
            self.kill()

    def generate_position(self):
        width = random.choice(
            [width for width in range(25, SCREEN_WIDTH + 1, 50)]
        )
        height = random.choice(
            [height for height in range(25, SCREEN_HEIGHT + 1, 50)]
        )
        if not self.walls_collide_point((width, height)):
            return width, height
        else:
            return random.choice(((25, 25), (25, 625), (625, 25), (625, 625)))

    def walls_collide_point(self, point):
        for sprite in self.engine.groups["walls"].sprites():
            if sprite.rect.collidepoint(point):
                return True
        return False


class Player(EngineMovingSprite):
    def __init__(self):
        super(Player, self).__init__()
        self.engine.add_to_group(self, "player")
        self.engine.add_to_group(self, "__flammable")
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


class Bomb(EngineSprite):
    def __init__(self, owner_center):
        super().__init__()
        self.engine.add_to_group(self, "bombs")
        self.surf = pygame.image.load("images/bomb.png").convert_alpha()
        self.lifetime = BOMB_TIMER
        self.explode_range = BOMB_EXPLODE_RANGE
        self.rect = self.surf.get_rect(
            center=self.get_self_center(owner_center)
        )

    def get_self_center(self, owner_center):
        lines = self.get_line_bomb_placed(owner_center)
        return (
            lines[0] * DEFAULT_OBJ_SIZE + self.surf.get_width() // 2,
            lines[1] * DEFAULT_OBJ_SIZE + self.surf.get_height() // 2,
        )

    @staticmethod
    def get_line_bomb_placed(owner_center):
        width = owner_center[0] // DEFAULT_OBJ_SIZE
        height = owner_center[1] // DEFAULT_OBJ_SIZE
        return width, height

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

        # kill all __flammable units that touch the fire
        flamed = pygame.sprite.spritecollideany(
            self, self.engine.groups["__flammable"]
        )
        if flamed:
            flamed.kill()


class Rock(EngineSprite):
    def __init__(self, owner_center):
        super().__init__()
        self.engine.add_to_group(self, "rocks")
        self.engine.add_to_group(self, "__flammable")
        self.surf = pygame.image.load("images/rock.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=self.get_self_center(owner_center)
        )

    def get_self_center(self, owner_center):
        lines = self.get_line_bomb_placed(owner_center)
        return (
            lines[0] * DEFAULT_OBJ_SIZE + self.surf.get_width() // 2,
            lines[1] * DEFAULT_OBJ_SIZE + self.surf.get_height() // 2,
        )

    @staticmethod
    def get_line_bomb_placed(owner_center):
        width = owner_center[0] // DEFAULT_OBJ_SIZE
        height = owner_center[1] // DEFAULT_OBJ_SIZE
        return width, height


class CreateEnemy(ABC):
    enemies = []

    @classmethod
    def add_enemy(cls, cls_):
        if cls_ not in cls.enemies:
            cls.enemies.append(cls_)

    @classmethod
    def spawn_random_enemy(cls):
        spawn_weight_spider = cls.enemies[0].spawn_weight
        spawn_weight_bird = cls.enemies[1].spawn_weight
        spawn_weight_boar = cls.enemies[2].spawn_weight
        random.choices(
            cls.enemies,
            weights=[
                spawn_weight_spider,
                spawn_weight_bird,
                spawn_weight_boar
            ])[0]()


@CreateEnemy.add_enemy
class Spider(Enemy):
    spawn_weight = 5

    def __init__(self):
        super().__init__()
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
        self.position = self.generate_position()
        self.rect = self.surf.get_rect(center=self.position[:2])

    def update(self):
        super().update()

    def move(self):
        player = self.engine.player
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


@CreateEnemy.add_enemy
class Bird(Enemy):
    spawn_weight = 2

    def __init__(self):
        super().__init__()
        self.image_left = pygame.image.load(
            "images/bird_left.png"
        ).convert_alpha()
        self.image_right = pygame.image.load(
            "images/bird_right.png"
        ).convert_alpha()
        self.surf = self.image_right
        self.plant_bomb_cooldown = PLANT_BOMB_COOLDOWN_BIRD
        self.position = self.generate_position()
        self.rect = self.surf.get_rect(center=self.position[:2])

    def update(self):
        super().update()
        if not pygame.sprite.spritecollideany(
                self, self.engine.groups["walls"]):
            self.i_am_bird()

    def move(self):
        player = self.engine.player
        x_diff = self.rect.centerx - player.rect.centerx
        y_diff = self.rect.centery - player.rect.centery

        if not y_diff:
            pass
        elif y_diff < 0:
            self.surf = self.image_left
            self.rect.move_ip(0, self.speed)
        else:
            self.surf = self.image_right
            self.rect.move_ip(0, -self.speed)
        if not x_diff:
            pass
        elif x_diff < 0:
            self.surf = self.image_right
            self.rect.move_ip(self.speed, 0)
        else:
            self.surf = self.image_left
            self.rect.move_ip(-self.speed, 0)

    def i_am_bird(self):
        """Bird says I'm bird and plant the bomb"""
        if self.plant_bomb_cooldown:
            self.plant_bomb_cooldown -= 1
        self.place_bomb()

    def place_bomb(self):
        if not self.plant_bomb_cooldown:
            pygame.mixer.music.load("sounds/im-a-bird.mp3")
            pygame.mixer.music.play(loops=1)
            Bomb(self.rect.center)
            self.plant_bomb_cooldown = PLANT_BOMB_COOLDOWN_BIRD


@CreateEnemy.add_enemy
class Boar(Enemy):
    spawn_weight = 3

    def __init__(self):
        super().__init__()
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
        self.is_on_rock = False
        self.surf = self.image_right
        self.plant_rock_cooldown = PLANT_ROCK_COOLDOWN_BOAR
        self.position = self.generate_position()
        self.rect = self.surf.get_rect(center=self.position[:2])

    def update(self):
        super().update()

        if self.plant_rock_cooldown:
            self.plant_rock_cooldown -= 1

        if not pygame.sprite.spritecollideany(
                self,
                self.engine.groups["rocks"]
        ):
            self.is_on_rock = False

        self.i_am_rock()

    def move(self):
        player = self.engine.player
        x_diff = self.rect.centerx - player.rect.centerx
        y_diff = self.rect.centery - player.rect.centery

        if not y_diff:
            pass
        elif y_diff < 0:
            self.surf = self.image_left
            self.rect.move_ip(0, self.speed)
            if not self.is_on_rock:
                self.move_collision_out(0, self.speed)
        else:
            self.surf = self.image_right
            self.rect.move_ip(0, -self.speed)
            if not self.is_on_rock:
                self.move_collision_out(0, -self.speed)
        if not x_diff:
            pass
        elif x_diff < 0:
            self.surf = self.image_right
            self.rect.move_ip(self.speed, 0)
            if not self.is_on_rock:
                self.move_collision_out(self.speed, 0)
        else:
            self.surf = self.image_left
            self.rect.move_ip(-self.speed, 0)
            if not self.is_on_rock:
                self.move_collision_out(-self.speed, 0)

    def i_am_rock(self):
        """Boar says I'm rock and plant the rock"""
        if not self.plant_rock_cooldown:
            self.is_on_rock = True
            pygame.mixer.music.load("sounds/Rock - I am Rock.mp3")
            pygame.mixer.music.play(loops=1)
            Rock(self.rect.center)
            self.plant_rock_cooldown = PLANT_ROCK_COOLDOWN_BOAR


class CreateEffect(ABC):
    effects = []

    @classmethod
    def add_effect(cls, cls_):
        if cls_ not in cls.effects:
            cls.effects.append(cls_)

    @classmethod
    def spawn_random_effect(cls):
        spawn_weight_heal = cls.effects[0].spawn_weight
        spawn_weight_slow = cls.effects[1].spawn_weight
        spawn_weight_fast = cls.effects[2].spawn_weight
        spawn_weight_remove_walls = cls.effects[3].spawn_weight
        random.choices(
            cls.effects,
            weights=[
                spawn_weight_heal,
                spawn_weight_slow,
                spawn_weight_fast,
                spawn_weight_remove_walls
            ])[0]()


@CreateEffect.add_effect
class Heal(Effect):
    spawn_weight = 5

    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load(
            "images/healing_effect.png"
        ).convert_alpha()
        self.rect = self.surf.get_rect(center=super().generate_position())

    def set_effect(self):
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            self.engine.player.health += 10


@CreateEffect.add_effect
class Slow(Effect):
    spawn_weight = 5

    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load(
            "images/slow_effect.png"
        ).convert_alpha()
        self.rect = self.surf.get_rect(center=super().generate_position())

    def set_effect(self):
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            self.engine.player.speed -= 1


@CreateEffect.add_effect
class Fast(Effect):
    spawn_weight = 5

    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load(
            "images/fast_effect.png"
        ).convert_alpha()
        self.rect = self.surf.get_rect(center=super().generate_position())

    def set_effect(self):
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            self.engine.player.speed += 1


@CreateEffect.add_effect
class RemoveWalls(Effect):
    """Effect invisible walls"""
    spawn_weight = 1

    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load(
            "images/wall_effect.png"
        ).convert_alpha()
        self.lifetime = 10
        self.rect = self.surf.get_rect(center=super().generate_position())

    def update(self):
        super().update()
        self.lifetime -= 1
        if self.lifetime == 0:
            self.spawn_weight = 1
            self.engine.hide_walls = False

    def set_effect(self):
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            self.engine.hide_walls = True
            self.spawn_weight = 0
