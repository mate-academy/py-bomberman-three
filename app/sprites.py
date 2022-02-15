import random
import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from mixins import MovingMixin, EngineMixin
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_OBJ_SIZE


class EngineSprite(EngineMixin, pygame.sprite.Sprite):
    pass


class EngineMovingSprite(EngineMixin, MovingMixin, pygame.sprite.Sprite):
    pass


class Player(EngineMovingSprite):
    def __init__(self):
        super(Player, self).__init__()
        self.engine.add_to_group(self, "player")
        self.speed = 5
        self.surf = pygame.image.load("images/player_front.png").convert_alpha()
        self.rect = self.surf.get_rect()
        self.placed_bomb_clock = 0
        self.on_bomb = False
        self.health = 100

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if self.health <= 0:
            self.kill()

        if pygame.sprite.spritecollideany(self, self.engine.groups["fires"]):
            self.kill()
            self.engine.running = False

        if self.placed_bomb_clock:
            self.placed_bomb_clock -= 1

        if not pygame.sprite.spritecollideany(self, self.engine.groups["bombs"]):
            self.on_bomb = False

        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
            self.surf = pygame.image.load("images/player_back.png").convert_alpha()

        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
            self.surf = pygame.image.load("images/player_front.png").convert_alpha()

        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)
            self.surf = pygame.image.load("images/player_left.png").convert_alpha()

        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)
            self.surf = pygame.image.load("images/player_right.png").convert_alpha()

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
        if not self.placed_bomb_clock:
            self.on_bomb = True
            Bomb(self.rect.center)
            self.placed_bomb_clock = 60


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
        self.rect = self.surf.get_rect(center=owner_center)
        self.rect.center = self.get_self_center()
        self.lifetime = 90
        self.explode_range = 5

    def get_self_center(self):
        lines = self.get_line_bomb_placed()
        return (
            lines[0] * DEFAULT_OBJ_SIZE + self.rect.width // 2,
            lines[1] * DEFAULT_OBJ_SIZE + self.rect.height // 2,
        )

    def update(self):
        self.lifetime -= 1
        if not self.lifetime:
            self.explode()

    def explode(self):
        fires = [(self.rect.centerx, self.rect.centery)]
        width = self.rect.centerx
        for it in range(1, self.explode_range + 1):
            height = self.rect.centery + it * DEFAULT_OBJ_SIZE
            sprite = self.create_test_sprite((width, height))
            if pygame.sprite.spritecollideany(sprite, self.engine.groups["walls"]):
                sprite.kill()
                break
            else:
                sprite.kill()
                Fire((width, height))
            height = self.rect.centery - it * DEFAULT_OBJ_SIZE
            sprite = self.create_test_sprite((width, height))
            if pygame.sprite.spritecollideany(sprite, self.engine.groups["walls"]):
                sprite.kill()
                break
            else:
                sprite.kill()
                Fire((width, height))

        height = self.rect.centery
        for it in range(1, self.explode_range + 1):
            width = self.rect.centerx + it * DEFAULT_OBJ_SIZE
            sprite = self.create_test_sprite((width, height))
            if pygame.sprite.spritecollideany(sprite, self.engine.groups["walls"]):
                sprite.kill()
                break
            else:
                sprite.kill()
                Fire((width, height))
            width = self.rect.centerx - it * DEFAULT_OBJ_SIZE
            sprite = self.create_test_sprite((width, height))
            if pygame.sprite.spritecollideany(sprite, self.engine.groups["walls"]):
                sprite.kill()
                break
            else:
                sprite.kill()
                Fire((width, height))

        for item in fires:
            Fire(item)
        self.kill()

    @staticmethod
    def create_test_sprite(center_pos: tuple):
        sprite = pygame.sprite.Sprite()
        sprite.surf = pygame.Surface((1, 1))
        sprite.rect = sprite.surf.get_rect(center=center_pos)
        return sprite

    def get_line_bomb_placed(self):
        width = self.rect.centerx // DEFAULT_OBJ_SIZE
        height = self.rect.centery // DEFAULT_OBJ_SIZE
        return width, height


class Fire(EngineSprite):
    def __init__(self, center_pos: tuple):
        super().__init__()
        self.engine.add_to_group(self, "fires")
        self.width = DEFAULT_OBJ_SIZE
        self.height = DEFAULT_OBJ_SIZE
        self.surf = pygame.image.load("images/explosion_1.png").convert_alpha()
        self.rect = self.surf.get_rect(center=(center_pos[0], center_pos[1]))
        self.lifetime = 10

    def update(self):
        self.lifetime -= 1
        if self.lifetime < 0:
            self.kill()
        elif self.lifetime < 3:
            self.surf = pygame.image.load("images/explosion_3.png").convert_alpha()
        elif self.lifetime < 6:
            self.surf = pygame.image.load("images/explosion_2.png").convert_alpha()


class Enemy(EngineMovingSprite):
    def __init__(self, width=45, height=45):
        super().__init__()
        self.width = width
        self.height = height
        self.engine.add_to_group(self, "enemies")
        self.surf = pygame.Surface((width, height))
        self.position = self.generate_position()
        self.rect = self.surf.get_rect(center=self.position[:2])
        self.speed = 2
        self.image_front = "images/spider_front.png"
        self.image_back = "images/spider_back.png"
        self.image_left = "images/spider_left.png"
        self.image_right = "images/spider_right.png"

    def update(self):
        self.collisions_handling()
        self.move()

    def collisions_handling(self):
        player = self.engine.groups["player"].sprites()[0]
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            player.health -= 10
            self.kill()
        if pygame.sprite.spritecollideany(self, self.engine.groups["fires"]):
            self.kill()

    def move(self):
        player = self.engine.groups["player"].sprites()[0]
        x_diff = self.rect.centerx - player.rect.centerx
        y_diff = self.rect.centery - player.rect.centery

        if not y_diff:
            pass
        elif y_diff < 0:
            self.surf = pygame.image.load(self.image_front).convert_alpha()
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
        else:
            self.surf = pygame.image.load(self.image_back).convert_alpha()
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
        if not x_diff:
            pass
        elif x_diff < 0:
            self.surf = pygame.image.load(self.image_right).convert_alpha()
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)
        else:
            self.surf = pygame.image.load(self.image_left).convert_alpha()
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)

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
