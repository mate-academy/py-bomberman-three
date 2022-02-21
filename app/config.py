from collections import namedtuple


SCREEN_WIDTH = 650
SCREEN_HEIGHT = 650
FRAMES_PER_SECOND = 60
BACKGROUND_COLOR = (0, 0, 0)

DEFAULT_OBJ_SIZE = 50
DEFAULT_PLAYER_HP = 100
DEFAULT_PLAYER_SPEED = 5

BOMB_TIMER = 90
PLANT_BOMB_COOLDOWN = 60
BOMB_EXPLODE_RANGE = 5
FIRE_LIFETIME = 10

ROCK_SPAWN_COOLDOWN = 300

HEALING_EFFECT = 20
SLOW_EFFECT = 2
ACCELERATE_EFFECT = 2

EnemyConstants = namedtuple(
    'EnemyConstants',
    'group_name group_speed group_images group_score group_damage',
)
BirdConstants = EnemyConstants(
    group_name='bird',
    group_speed=1,
    group_images={
        'front': "images/bird_right.png",
        'back': "images/bird_right.png",
        'right': "images/bird_right.png",
        'left': "images/bird_left.png",
    },
    group_score=20,
    group_damage=5
)

BoarConstants = EnemyConstants(
    group_name='boar',
    group_speed=5,
    group_images={
        'front': "images/boar_front.png",
        'back': "images/boar_back.png",
        'right': "images/boar_right.png",
        'left': "images/boar_left.png",
    },
    group_score=20,
    group_damage=5
)
SpiderConstants = EnemyConstants(
    group_name='spider',
    group_speed=5,
    group_images={
        'front': "images/spider_front.png",
        'back': "images/spider_back.png",
        'right': "images/spider_right.png",
        'left': "images/spider_left.png",
    },
    group_score=20,
    group_damage=5
)
