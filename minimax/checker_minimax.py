from copy import deepcopy
from core.game_state import GameState
from core.board import Board, PieceMove
from core.piece import PieceSide
import logging
import time

logger = logging.getLogger(__name__)

class CheckerMinimax:
    def __init__(self, max_depth:int, time_limit_sec:int, alpha_beta:bool = True):
        self.max_depth = max_depth
        self.time_limit = time_limit_sec
        self.start_time = time.time()
        self.alpha_beta = alpha_beta

    def find_best_checker_move(self, board: Board)->tuple[PieceMove, Board]:
        self.start_time = time.time()
        
        best_move = None
        best_state = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        for move, board_state in board.get_all_moves_with_nodes(PieceSide.COMPUTER):        
            score, _ = self._minimax(board_state, self.max_depth - 1, alpha=alpha, beta=beta, max_player=False)
            if score > best_score:
                logger.debug(f"Best score: {score}")
                best_score = score
                best_move = move            
                best_state = board_state
            if self.alpha_beta:
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
        if best_move is None or best_state is None:
            raise Exception("Best move not found")
        
        return best_move, best_state
    
    def _minimax(self, game_state: GameState, depth:int, alpha:float, beta:float, max_player:bool)->tuple[int|float, GameState]:
        if depth == 0 or game_state.winner() != None or time.time() - self.start_time > self.time_limit:
            if time.time() - self.start_time > self.time_limit:
                logger.debug("Time limit reached")
            return game_state.heuristic(), game_state
        try:
            if max_player:
                maxEval = float('-inf')
                best_move = None
                for move in game_state.get_all_moves(PieceSide.COMPUTER):
                    evaluation = self._minimax(move, depth-1, alpha, beta, False)[0]
                    if evaluation > maxEval:
                        maxEval = evaluation
                        best_move = move
                    if self.alpha_beta:
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
                    evaluation = self._minimax(move, depth-1, alpha, beta, True)[0]
                    if evaluation < minEval:
                        minEval = evaluation
                        best_move = move
                    if self.alpha_beta:
                        beta = min(beta, evaluation)
                        if beta <= alpha:
                            break
                if not best_move:
                    return game_state.heuristic(), game_state
                return minEval, best_move
        except Exception as e:
            return game_state.heuristic(), game_state