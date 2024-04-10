from core.board import Board
from core.piece import PieceSide, Piece
from game.game_context import GameContext
from game.board_renderer import BoardRenderer
from game.game_controller import GameController
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

game_controller = GameController(board, game_context)
game_controller.run()