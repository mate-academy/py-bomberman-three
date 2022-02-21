import pygame

# engine
SCREEN_WIDTH = 650
SCREEN_HEIGHT = 650
BACKGROUND_COLOR = (0, 0, 0)
FRAMES_PER_SECOND = 60
DEFAULT_OBJ_SIZE = 50

# player
DEFAULT_PLAYER_HP = 100
DEFAULT_PLAYER_SPEED = 4

# score
DEFAULT_SCORE_INCREASE = 10

# bomb
BOMB_TIMER = 90
BOMB_COOLDOWN = 45
EXPLOSION_RANGE = 2

# events
ADDENEMY = pygame.USEREVENT + 1
DEFAULT_EVENT_TIMEOUT = 3000

# effects
DEFAULT_HEALTH_BONUS = 20
CHANCE_DROP = 0.15
SPEED_BOOST_FACTOR = 1
