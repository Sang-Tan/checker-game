import pygame

WIDTH, HEIGHT = 690, 690
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH//COLS

# rgb
# RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128,128,128)

# game color
COL_PLAYER = (171, 179, 181)
COL_AI = (159, 10, 11)
COL_BOARD_PATTERN_1 = (237, 160, 82)
COL_BOARD_PATTERN_2 = (81, 71, 72)


CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (44, 25))
