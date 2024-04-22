from core.board import Board
from game.game_context import GameContext, GameEventType
from game.game_board import GameBoard
from game.game_controller import BoardGameController
from game.main_panel import MainPanel
import configparser
import logging
import sys
import pygame
import os

BOARD_SIZE_MIN = 8
BOARD_SIZE_MAX = float('inf')

# WINDOWS_WIDTH = 1000
# WINDOWS_HEIGHT = 800
# BOARD_WIDTH = 800
# BOARD_HEIGHT = 800
# PANEL_WIDTH = 200
# PANEL_HEIGHT = 800

config = configparser.ConfigParser()
config.read("game_config.ini")

board_size = BOARD_SIZE_MIN

pygame.init()

# log to console
logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)

logger = logging.getLogger(__name__)

board = Board(board_size, board_size)
game_context = GameContext()
game_context.initialize(os.getcwd(), {s:dict(config.items(s)) for s in config.sections()})

board_width = int(game_context.get_config()["WINDOW"]["board-width"])
board_height = int(game_context.get_config()["WINDOW"]["board-height"])
panel_width = int(game_context.get_config()["WINDOW"]["panel-width"])
panel_height = int(game_context.get_config()["WINDOW"]["panel-height"])

game_board = GameBoard(board, 0, 0, board_width, board_height)
main_panel = MainPanel(board_width, 0, panel_width, panel_height)
main_panel.set_size_text(f"{board_size}x{board_size}")
main_panel.draw()


game_controller = BoardGameController(board, game_board, game_context)

def restart():
    global board, game_board, game_controller
    
    board = Board(board_size, board_size)
    game_board = GameBoard(board, 0, 0, board_width, board_height)
    game_controller = BoardGameController(board, game_board, game_context)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
            
    while game_context.has_event():
        event = game_context.pop_event()
        if event.get_type() == GameEventType.RESTART:
            logger.debug("Restart event received")
            restart()
        elif event.get_type() == GameEventType.CHANGE_TURN:
            logger.debug("Change turn event received")
            data = event.get_data()
            main_panel.set_turn_text(data)
        elif event.get_type() == GameEventType.CHANGE_SIZE:
            new_size = board_size + event.get_data()
            if new_size >= BOARD_SIZE_MIN and new_size <= BOARD_SIZE_MAX:
                board_size = new_size
                main_panel.set_size_text(f"{board_size}x{board_size}")
            
    game_board.update(events=events)
    game_controller.update(events=events)
    main_panel.update(events=events)
    pygame.display.update()
    pygame.time.Clock().tick(60)
