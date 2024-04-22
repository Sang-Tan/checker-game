from core.board import Board, PieceMove
from core.piece import PieceSide
from game.game_context import GameContext, GameEvent, GameEventType
from game.game_board import GameBoard
from game.game_object import GameObject
from minimax.checker_minimax import CheckerMinimax
from abc import ABC, abstractmethod
from enum import Enum
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import logging
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
        game_config = GameContext().get_config()["GAME"]     
        logger.debug("ComputerGameState init")
        self.context = context
        self.cur_moves:deque[Board] = deque()
        self.counter = 0
        self.checker_minimax = CheckerMinimax(int(game_config["computer-max-depth"]), 
                                              int(game_config["computer-limit-sec"]),
                                              eval(game_config["computer-alpha-beta"]))
        
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.running = False
        
        super().__init__()
    
    def update(self, events: list[pygame.event.Event] = []):
        if self.running:
            return
        
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
        self.running = True
        cur_board = self.context.get_board()
        
        future = self.executor.submit(self._calculate_best_moves, cur_board)
        future.add_done_callback(lambda future: self._handle_best_moves(*future.result()))
        
    def _calculate_best_moves(self, cur_state: Board)->tuple[PieceMove, Board, Board]:
        logger.debug("Computer start thinking")
        best_move, best_state = self.checker_minimax.find_best_checker_move(cur_state)
        
        return best_move, best_state, cur_state
    
    def _handle_best_moves(self, best_move: PieceMove, best_state: Board, cur_state: Board):
        try:
            logger.debug("Computer end thinking and start moving")
            moves = []
            move_pos = []
            while best_move:
                # ignore root move
                if not best_move.before:
                    break
                
                logger.debug(f"Move: {(best_move.row, best_move.col)}")
                move_pos.append((best_move.row, best_move.col))
                moves.append(cur_state.get_state_from_move(best_move))
                best_move = best_move.before
            
            move_pos.reverse()
            print(f"Computer moves: {move_pos}")
        
            moves.reverse()
            self.cur_moves.extend(moves)
        finally:
            self.running = False
                   
class BoardGameController(GameStateContext, GameObject):
    def __init__(self, board:Board, game_board: GameBoard, game_context: GameContext):
        # TODO: clean code
        self.board = board
        self.game_context = game_context
        self.game_board = game_board
        self.game_board.on_square_click = self._handle_square_click
        self.clock = pygame.time.Clock()
        self.current_state:GameState
        self._init_states()

    def get_state(self, state: GameStates)->GameState:
        return self.states[state]
    
    def set_state(self, state: GameStates):
        self.current_state = self.states[state]
        logger.debug(f"Set state: {state}")
        if state == GameStates.COMPUTER_TURN:
            self.game_context.push_event(GameEvent(GameEventType.CHANGE_TURN, "Computer"))
        else:
            self.game_context.push_event(GameEvent(GameEventType.CHANGE_TURN, "Player"))
        
    def get_board(self)->Board:
        return self.board
    
    def set_board(self, board: Board):
        self.board = board
        self.game_board.set_board(board)
    
    def get_board_renderer(self)->GameBoard:
        return self.game_board
    
    def update(self, events: list[pygame.event.Event] = []):
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
        self.set_state(GameStates.PLAYER_TURN)