from .algorithm import minimax
from copy import deepcopy
from core.game_state import GameState
from core.board import Board, PieceMove
from core.piece import PieceSide
import logging

logger = logging.getLogger(__name__)

def find_best_checker_move(board: Board, depth: int)->tuple[PieceMove, Board]:
    best_move = None
    best_state = None
    best_score = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    for move, board_state in board.get_all_moves_with_nodes(PieceSide.COMPUTER):        
        score, _ = minimax(board_state, depth - 1, alpha=alpha, beta=beta, max_player=False)
        if score > best_score:
            logger.debug(f"Best score: {score}")
            best_score = score
            best_move = move            
            best_state = board_state
            
        alpha = max(alpha, score)
        if beta <= alpha:
            break
    if best_move is None or best_state is None:
        raise Exception("Best move not found")
    
    return best_move, best_state