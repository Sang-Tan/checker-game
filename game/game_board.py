import pygame
import logging
from core.piece import PieceSide
from core.board import BoardData
from .game_context import GameContext
from .game_object import VisibleGameObject
from typing import Callable
import os

logger = logging.getLogger(__name__)

SQUARE_COLOR_1 = (76, 50, 20)
SQUARE_COLOR_2 = (102, 73, 27)
MARKER_COLOR = (255, 0, 0)

PLAYER_PIECE_IMG = 'assets/black_piece.png'
PLAYER_KING_IMG = 'assets/black_king.png'
OPPONENT_PIECE_IMG = 'assets/white_piece.png'
OPPONENT_KING_IMG = 'assets/white_king.png'
    
class GameBoard(VisibleGameObject):
    def __init__(self, board_data: BoardData,
                 board_left:int, board_top:int, board_width:int, board_height:int,
                 on_square_click:Callable[[tuple[int, int]], None] = lambda x: None):
        super().__init__(board_left, board_top, board_width, board_height)
        self.screen_context = GameContext()
        self.on_square_click = on_square_click
        self.markers:list[tuple[int, int]] = []
        self._set_board(board_data)
        self._load_images(self.screen_context.get_root_path())
        self.draw()
        
        
    def update(self, events: list[pygame.event.Event] = []):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = self._get_local_mouse_pos()
                logger.debug(f"Mouse clicked at {mouse_x}, {mouse_y}")
                square_coor = self.get_square_coor_by_pos(mouse_x, mouse_y)
                if square_coor is not None:
                    logger.debug(f"Square clicked at {square_coor}")
                    self.on_square_click(square_coor)
        
    def set_board(self, board_data: BoardData):
        self._set_board(board_data)
        self.draw()
        
    def draw(self):
        self._draw_squares()
        self._draw_pieces()
        self._draw_markers()
        
    def set_markers(self, markers:list[tuple[int, int]]):
        self.clear_markers()                
        self.markers = markers
        self._draw_markers()
        
    def clear_markers(self):
        board_rect = self.rect
        square_width = board_rect.width / self.board_size
        square_height = board_rect.height / self.board_size
        for row, col in self.markers:
            self._draw_square(row, col, square_width, square_height)
            
        self.markers = []
            
    def get_square_coor_by_pos(self, x:int, y:int)->tuple[int, int] | None:
        board_rect = self.rect
        square_width = board_rect.width // self.board_size
        square_height = board_rect.height // self.board_size
        if not board_rect.collidepoint(x, y):
            return None
        col = (x - board_rect.left) // square_width
        row = (y - board_rect.top) // square_height
        
        return row, col

    def _set_board(self, board_data: BoardData):
        self.board = board_data
        self.board_size = board_data.get_size()

    def _load_images(self, root_path:str):
        square_width = self.rect.width // self.board_size
        square_height = self.rect.height // self.board_size
        piece_width = int(square_width / 2)
        piece_height = int(square_height / 2)
        
        self.player_piece_img = pygame.image.load(os.path.join(root_path, PLAYER_PIECE_IMG))
        self.player_piece_img = pygame.transform.scale(self.player_piece_img, (piece_width, piece_height))
        
        self.player_king_img = pygame.image.load(os.path.join(root_path, PLAYER_KING_IMG))
        self.player_king_img = pygame.transform.scale(self.player_king_img, (piece_width, piece_height))
        
        self.opponent_piece_img = pygame.image.load(os.path.join(root_path, OPPONENT_PIECE_IMG))
        self.opponent_piece_img = pygame.transform.scale(self.opponent_piece_img, (piece_width, piece_height))
        
        self.opponent_king_img = pygame.image.load(os.path.join(root_path, OPPONENT_KING_IMG))
        self.opponent_king_img = pygame.transform.scale(self.opponent_king_img, (piece_width, piece_height))
        
    def _draw_squares(self):
        square_width = self.rect.width / self.board_size
        square_height = self.rect.height / self.board_size
        for row in range(self.board_size):
            for col in range(self.board_size):
                self._draw_square(row, col, square_width, square_height)
                
    def _draw_square(self, row:int, col:int, square_width:float, square_height:float):        
        square_rect = self._get_square_rect(row, col, square_width, square_height)
        square_color = SQUARE_COLOR_1 if (row + col) % 2 == 0 else SQUARE_COLOR_2
        pygame.draw.rect(self.screen_context.get_window(), square_color, square_rect)
                
    def _draw_pieces(self):
        board_rect = self.rect
        square_width = board_rect.width / self.board_size
        square_height = board_rect.height / self.board_size
        for row in range(self.board_size):
            for col in range(self.board_size):
                self._draw_piece(row, col, board_rect, square_width, square_height)
                
    def _draw_piece(self, row:int, col:int, board_rect:pygame.Rect, square_width:float, square_height:float):
        square_rect = self._get_square_rect(row, col, square_width, square_height)
        piece = self.board[row][col]
        if piece is None:
            return
        if piece.side == PieceSide.PLAYER:
            piece_image = self.player_piece_img if not piece.king else self.player_king_img
        else:
            piece_image = self.opponent_piece_img if not piece.king else self.opponent_king_img

        piece_rect = piece_image.get_rect()
        piece_rect.center = (
            int(square_rect.left + square_rect.width / 2),
            int(square_rect.top + square_rect.height / 2)
        )
        self.screen_context.get_window().blit(piece_image, piece_rect)
                
    def _get_square_rect(self, row:int, col:int, square_width:float, square_height:float)->pygame.Rect:
        pivot_x, pivot_y = self.rect.topleft
        start_x = int(pivot_x + col * square_width)
        start_y = int(pivot_y + row * square_height)
        next_x = int(pivot_x + (col + 1) * square_width)
        next_y = int(pivot_y + (row + 1) * square_height)
        draw_width = next_x - start_x
        draw_height = next_y - start_y    
        
        return pygame.Rect(
            int(start_x),
            int(start_y),
            draw_width,
            draw_height
        )
    
    def _draw_markers(self):
        board_rect = self.rect
        square_width = board_rect.width / self.board_size
        square_height = board_rect.height / self.board_size
        for row, col in self.markers:
            marker_rect = self._get_square_rect(row, col, square_width, square_height)
            pygame.draw.rect(self.screen_context.get_window(), MARKER_COLOR, marker_rect)