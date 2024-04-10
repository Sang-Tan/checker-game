from core.board import Board
from game.game_context import GameContext, GameEventType
from game.game_board import GameBoard
from game.game_controller import BoardGameController
from game.main_panel import MainPanel
import logging
import sys
import pygame
import os

BOARD_SIZE = 4

pygame.init()

# log to console
logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)

logger = logging.getLogger(__name__)

board = Board(BOARD_SIZE, BOARD_SIZE)
game_context = GameContext()
game_context.initialize(1000, 800, os.getcwd())

game_board = GameBoard(board, 0, 0, 800, 800)
main_panel = MainPanel(800, 0, 200, 800)
main_panel.draw()
game_controller = BoardGameController(board, game_board, game_context)

def restart():
    global board, game_board, game_controller
    
    board = Board(BOARD_SIZE, BOARD_SIZE)
    game_board = GameBoard(board, 0, 0, 800, 800)
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
            main_panel.draw_turn_text(data)
            
    game_board.update(events=events)
    game_controller.update(events=events)
    main_panel.update(events=events)
    pygame.display.update()
    pygame.time.Clock().tick(60)
