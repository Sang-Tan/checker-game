from copy import deepcopy
from checkers.board import Board
from checkers.game_state import GameState
import pygame

RED = (255,0,0)
WHITE = (255, 255, 255)

def minimax(game_state: GameState, depth, max_player:bool, game):
    if depth == 0 or game_state.winner() != None:
        return game_state.evaluate(), game_state
    
    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(game_state, WHITE, game):
            evaluation = minimax(move, depth-1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(game_state, RED, game):
            evaluation = minimax(move, depth-1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        
        return minEval, best_move


def simulate_move(piece, move, board, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove(skip)

    return board


def get_all_moves(game_state: GameState, color):
    moves = []

    for piece in game_state.get_all_pieces(color):
        valid_moves = game_state.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            temp_board = deepcopy(game_state)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, skip)
            moves.append(new_board)
    
    return moves