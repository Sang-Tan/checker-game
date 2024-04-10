from core.board import Board
from core.piece import PieceSide
from game.game_context import GameContext
from game.game_board import GameBoard
from game.game_object import GameObject
from minimax.checker_minimax import find_best_checker_move
from abc import ABC, abstractmethod
from enum import Enum
from collections import deque
import logging
import sys
import pygame

logger = logging.getLogger(__name__)

class GameState:
    @abstractmethod
    def update(self, events: list[pygame.event.Event] = []):
        pass
    
class GameStates(Enum):
    PLAYER_TURN = 0
    COMPUTER_TURN = 1
    
class GameStateContext(ABC):
    @abstractmethod
    def get_state(self, state: GameStates)->GameState:
        pass
    
    @abstractmethod
    def set_state(self, state: GameStates):
        pass
    
    @abstractmethod
    def get_board(self)->Board:
        pass
    
    @abstractmethod
    def set_board(self, board: Board):
        pass
    
    @abstractmethod
    def get_board_renderer(self)->GameBoard:
        pass
    
class PlayerGameState(GameState):
    class SquareState(Enum):
        EMPTY = 0
        PLAYER = 1
        OPPONENT = 2
        MARKER = 3
        
    def __init__(self, context: GameStateContext):
        self.context = context
        self.possible_player_moves = {}
        self.last_selected_piece = None
        self.pending_mouse = None
        super().__init__()
    
    def update(self, events: list[pygame.event.Event] = []):
        if self.pending_mouse:
            self._handler_player_mouse(self.pending_mouse)
            self.pending_mouse = None

    def pending_player_mouse(self, square_clicked:tuple[int, int]):
        self.pending_mouse = square_clicked

    def _handler_player_mouse(self, square_clicked:tuple[int, int]):
        cur_board = self.context.get_board()
        cur_renderer = self.context.get_board_renderer()
        if square_clicked:
            piece = cur_board.get_piece(*square_clicked)
        
            if square_clicked in self.possible_player_moves:
                square_state = self.SquareState.MARKER
            elif not piece: 
                square_state = self.SquareState.EMPTY
            elif piece.side == PieceSide.PLAYER:
                square_state = self.SquareState.PLAYER
            else:
                square_state = self.SquareState.OPPONENT
        
            if square_state == self.SquareState.PLAYER:
                piece = cur_board.get_piece(*square_clicked)
                if not piece:
                    raise Exception("Invalid piece")
            
                moves = cur_board.get_valid_moves(piece)
                moves_pos = list(moves.keys())
                markers_pos = []
                for move_pos in moves_pos:
                    logger.debug(f"Move pos: {move_pos}")
                    markers_pos.append(move_pos)
                
                self.last_selected_piece = piece
                self.possible_player_moves = moves
                cur_renderer.set_markers(markers_pos)
            elif square_state == self.SquareState.MARKER:
                if self.last_selected_piece:
                    cur_renderer.clear_markers()
                    logger.debug(f"Moving piece: {self.last_selected_piece} to {square_clicked}")
                    jump = self.possible_player_moves[square_clicked]
                    if jump:
                        cur_board.remove(jump)
                    cur_board.move(self.last_selected_piece, square_clicked[0], square_clicked[1])
                    cur_renderer.set_board(cur_board)
                    self.possible_player_moves = {}
                    self.last_selected_piece = None
                    self.context.set_state(GameStates.COMPUTER_TURN)        
                self.last_selected_piece = None
            else:
                self.last_selected_piece = None
                cur_renderer.clear_markers()
                    
class ComputerGameState(GameState):
    MAX_COUNTER = 10
    
    def __init__(self, context: GameStateContext):
        logger.debug("ComputerGameState init")
        self.context = context
        self.cur_moves:deque[Board] = deque()
        self.counter = 0
        super().__init__()
    
    def update(self, events: list[pygame.event.Event] = []):
        if len(self.cur_moves) <= 0:
            self.get_best_moves()
        else:
            self.move()
    
    def move(self):
        logger.debug("Counter: %d", self.counter)
        if self.counter <= 0:
            move = self.cur_moves.popleft()
            self.context.set_board(move)
            
            if len(self.cur_moves) <= 0:
                logger.debug("Computer turn end")
                self.context.set_state(GameStates.PLAYER_TURN)
            else:
                logger.debug("Reset counter")
                self.counter = ComputerGameState.MAX_COUNTER
        else:
            self.counter -= 1
    
    def get_best_moves(self):
        logger.debug("Computer move")
        cur_board = self.context.get_board()
        best_move, best_state = find_best_checker_move(cur_board, 4)
        moves = []
        move_pos = []
        while best_move:
            # ignore root move
            if not best_move.before:
                break
            
            logger.debug(f"Move: {(best_move.row, best_move.col)}")
            move_pos.append((best_move.row, best_move.col))
            moves.append(cur_board.get_state_from_move(best_move))
            best_move = best_move.before
        
        move_pos.reverse()
        print(f"Computer moves: {move_pos}")
    
        moves.reverse()
        self.cur_moves.extend(moves)
                   
class BoardGameController(GameStateContext, GameObject):
    def __init__(self, board: Board, game_context: GameContext):
        self.board = board
        self.game_context = game_context
        self.game_board = GameBoard(self.board, self.game_context, self._handle_square_click)
        self.clock = pygame.time.Clock()
        self.current_state:GameState
        self._init_states()

    def get_state(self, state: GameStates)->GameState:
        return self.states[state]
    
    def set_state(self, state: GameStates):
        self.current_state = self.states[state]
        
    def get_board(self)->Board:
        return self.board
    
    def set_board(self, board: Board):
        self.board = board
        self.game_board.set_board(board)
    
    def get_board_renderer(self)->GameBoard:
        return self.game_board
    
    def update(self, events: list[pygame.event.Event] = []):
        self.game_board.update(events)
        self.current_state.update(events)
        
    def _handle_square_click(self, square_coor: tuple[int, int]):
        self.clicked_square = square_coor
        logger.debug(f"Square clicked: {square_coor}")
        if isinstance(self.current_state, PlayerGameState):
            self.current_state.pending_player_mouse(square_coor)
        
    def _init_states(self):
        self.states = {
            GameStates.PLAYER_TURN: PlayerGameState(self),
            GameStates.COMPUTER_TURN: ComputerGameState(self)
        }
        self.current_state = self.states[GameStates.PLAYER_TURN]