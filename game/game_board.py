import pygame
import logging
from core.piece import PieceSide
from core.board import BoardData
from .game_context import GameContext
from .game_object import VisibleGameObject
from enum import Enum
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
    def __init__(self, board_data: BoardData, screen_context:GameContext, on_square_click:Callable[[tuple[int, int]], None]):
        super().__init__(0, 0, screen_context.get_window().get_width(), screen_context.get_window().get_height())
        self.screen_context = screen_context
        self.on_square_click = on_square_click if on_square_click is not None else lambda x: None
        self.markers:list[tuple[int, int]] = []
        self._set_board(board_data)
        self._load_images(screen_context.get_root_path())
        self.draw()
        
        
    def update(self, events: list[pygame.event.Event] = []):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = self._get_local_mouse_pos()
                square_coor = self.get_square_coor_by_pos(mouse_x, mouse_y)
                if square_coor is not None:
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
        square_width = board_rect.width // self.board_size
        square_height = board_rect.height // self.board_size
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
        square_width = self.rect.width // self.board_size
        square_height = self.rect.height // self.board_size
        for row in range(self.board_size):
            for col in range(self.board_size):
                self._draw_square(row, col, square_width, square_height)
                
    def _draw_square(self, row:int, col:int, square_width:int, square_height:int):
        pos_x = self.rect.left
        pos_y = self.rect.top
        
        square_rect = pygame.Rect(
            pos_x + col * square_width,
            pos_y + row * square_height,
            square_width,
            square_height
        )
        square_color = SQUARE_COLOR_1 if (row + col) % 2 == 0 else SQUARE_COLOR_2
        pygame.draw.rect(self.screen_context.get_window(), square_color, square_rect)
                
    def _draw_pieces(self):
        board_rect = self.rect
        square_width = board_rect.width // self.board_size
        square_height = board_rect.height // self.board_size
        for row in range(self.board_size):
            for col in range(self.board_size):
                self._draw_piece(row, col, board_rect, square_width, square_height)
                
    def _draw_piece(self, row:int, col:int, board_rect:pygame.Rect, square_width:int, square_height:int):
        piece = self.board[row][col]
        piece_width = square_width // 2
        piece_height = square_height // 2
        if piece is None:
            return
        if piece.side == PieceSide.PLAYER:
            piece_image = self.player_piece_img if not piece.king else self.player_king_img
        else:
            piece_image = self.opponent_piece_img if not piece.king else self.opponent_king_img

        piece_rect = piece_image.get_rect()
        piece_rect.center = (
            int(board_rect.left + col * square_width + square_width / 2),
            int(board_rect.top + row * square_height + square_height / 2)
        )
        self.screen_context.get_window().blit(piece_image, piece_rect)
                
    def _draw_markers(self):
        board_rect = self.rect
        square_width = board_rect.width / self.board_size
        square_height = board_rect.height / self.board_size
        for row, col in self.markers:
            marker_rect = pygame.Rect(
                board_rect.left + col * square_width,
                board_rect.top + row * square_height,
                square_width,
                square_height
            )
            pygame.draw.rect(self.screen_context.get_window(), MARKER_COLOR, marker_rect)