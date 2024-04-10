from core.board import Board
from core.piece import PieceSide, Piece
from game.game_context import GameContext
from game.game_board import GameBoard
from game.game_controller import BoardGameController
from minimax.checker_minimax import find_best_checker_move
from enum import Enum
import logging
import sys
import pygame
import os

# log to console
logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)

logger = logging.getLogger(__name__)

board = Board(8, 8)
game_context = GameContext(800, 800, os.getcwd())

game_controller = BoardGameController(board, game_context)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
    game_controller.update(events=events)
    pygame.display.update()
    pygame.time.Clock().tick(60)
