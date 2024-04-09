from core.board import Board
from core.piece import PieceSide, Piece
from game.game_context import GameContext
from game.board_renderer import BoardRenderer
from minimax.algorithm import minimax
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

board_renderer = BoardRenderer(board, game_context)

last_selected_piece = None
possible_player_moves:dict[tuple[int, int], list[Piece]] = {}
player_turn = True

board_renderer.draw()
clock = pygame.time.Clock()

class SquareState(Enum):
    EMPTY = 0,
    PLAYER = 1,
    OPPONENT = 2,
    MARKER = 3

def move_computer():
    global board
    
    logger.debug("Computer move")
    best_move = minimax(board, 4, True)
    logger.debug(f"Best move: {best_move}")
    if not isinstance(best_move[1], Board):
        raise Exception("Type error")
    board = best_move[1]
    board_renderer.set_board(board)

def handler_player_mouse():
    global last_selected_piece, possible_player_moves, player_turn
    
    pos_x, pos_y = pygame.mouse.get_pos()
    square_clicked = board_renderer.get_square_coor_by_pos(pos_x, pos_y)
    if square_clicked:
        piece = board.get_piece(*square_clicked)
        
        if square_clicked in possible_player_moves:
            square_state = SquareState.MARKER
        elif not piece: 
            square_state = SquareState.EMPTY
        elif piece.side == PieceSide.PLAYER:
            square_state = SquareState.PLAYER
        else:
            square_state = SquareState.OPPONENT
        
        if square_state == SquareState.PLAYER:
            piece = board.get_piece(*square_clicked)
            if not piece:
                raise Exception("Invalid piece")
            
            moves = board.get_valid_moves(piece)
            moves_pos = list(moves.keys())
            markers_pos = []
            for move_pos in moves_pos:
                logger.debug(f"Move pos: {move_pos}")
                markers_pos.append(move_pos)
                
            last_selected_piece = piece
            possible_player_moves = moves
            board_renderer.set_markers(markers_pos)
        elif square_state == SquareState.MARKER:
            if last_selected_piece:
                board_renderer.clear_markers()
                logger.debug(f"Moving piece: {last_selected_piece} to {square_clicked}")
                jump = possible_player_moves[square_clicked]
                if jump:
                    board.remove(jump)
                board.move(last_selected_piece, square_clicked[0], square_clicked[1])
                board_renderer.set_board(board)
                player_turn = False
            last_selected_piece = None
        else:
            last_selected_piece = None
            board_renderer.clear_markers()

while True:
    clock.tick(60)
    if not player_turn:
        move_computer()
        player_turn = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            handler_player_mouse()
                    
    pygame.display.update()