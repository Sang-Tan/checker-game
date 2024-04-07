from copy import deepcopy
from core.game_state import GameState
from core.piece import PieceSide

def minimax(game_state: GameState, depth:int, max_player:bool)->tuple[int|float, GameState]:
    if depth == 0 or game_state.winner() != None:
        return game_state.heuristic(), game_state
    
    if max_player:
        maxEval = float('-inf')
        # best_move = None
        for move in game_state.get_all_moves(PieceSide.COMPUTER):
            evaluation = minimax(move, depth-1, False)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        
        return maxEval, best_move
    else:
        minEval = float('inf')
        # best_move = None
        for move in game_state.get_all_moves(PieceSide.PLAYER):
            evaluation = minimax(move, depth-1, True)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        
        return minEval, best_move

