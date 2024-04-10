from copy import deepcopy
from core.game_state import GameState
from core.piece import PieceSide

def minimax(game_state: GameState, depth:int, alpha:float, beta:float, max_player:bool)->tuple[int|float, GameState]:
    if depth == 0 or game_state.winner() != None:
        return game_state.heuristic(), game_state
    try:
        if max_player:
            maxEval = float('-inf')
            best_move = None
            for move in game_state.get_all_moves(PieceSide.COMPUTER):
                evaluation = minimax(move, depth-1, alpha, beta, False)[0]
                if evaluation > maxEval:
                    maxEval = evaluation
                    best_move = move
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            if not best_move:
                return game_state.heuristic(), game_state
            
            return maxEval, best_move
        else:
            minEval = float('inf')
            best_move = None
            for move in game_state.get_all_moves(PieceSide.PLAYER):
                evaluation = minimax(move, depth-1, alpha, beta, True)[0]
                if evaluation < minEval:
                    minEval = evaluation
                    best_move = move
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            if not best_move:
                return game_state.heuristic(), game_state
            return minEval, best_move
    except Exception as e:
        return game_state.heuristic(), game_state
