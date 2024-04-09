import pygame
import logging
from core.piece import PieceSide
from core.board import BoardData
from .game_context import GameContext
from enum import Enum
import os

logger = logging.getLogger(__name__)

SQUARE_COLOR_1 = (76, 50, 20)
SQUARE_COLOR_2 = (102, 73, 27)
PLAYER_PIECE_COLOR = (255, 255, 255)
OPPONENT_PIECE_COLOR = (0, 0, 0)
PLAYER_KING_COLOR = (255, 255, 0)
OPPONENT_KING_COLOR = (0, 0, 255)
MARKER_COLOR = (255, 0, 0)

PLAYER_PIECE_IMG = 'assets/black_piece.png'
PLAYER_KING_IMG = 'assets/black_king.png'
OPPONENT_PIECE_IMG = 'assets/white_piece.png'
OPPONENT_KING_IMG = 'assets/white_king.png'
    
class BoardRenderer:
    def __init__(self, board_data: BoardData, screen_context:GameContext):
        self.screen_context = screen_context
        self.markers:list[tuple[int, int]] = []
        self._load_images(screen_context.get_root_path())
        self.set_board(board_data)
        
    def set_board(self, board_data: BoardData):
        self.board = board_data
        self.board_size = board_data.get_size()
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
        board_rect = self.screen_context.get_board_rect()
        square_width = board_rect.width // self.board_size
        square_height = board_rect.height // self.board_size
        for row, col in self.markers:
            self._draw_square(row, col, board_rect, square_width, square_height)
            
        self.markers = []
            
    def get_square_coor_by_pos(self, x:int, y:int)->tuple[int, int] | None:
        board_rect = self.screen_context.get_board_rect()
        square_width = board_rect.width // self.board_size
        square_height = board_rect.height // self.board_size
        if not board_rect.collidepoint(x, y):
            return None
        col = (x - board_rect.left) // square_width
        row = (y - board_rect.top) // square_height
        
        return row, col

    def _load_images(self, root_path:str):
        self.player_piece_img = pygame.image.load(os.path.join(root_path, PLAYER_PIECE_IMG))
        self.player_king_img = pygame.image.load(os.path.join(root_path, PLAYER_KING_IMG))
        self.opponent_piece_img = pygame.image.load(os.path.join(root_path, OPPONENT_PIECE_IMG))
        self.opponent_king_img = pygame.image.load(os.path.join(root_path, OPPONENT_KING_IMG))
        
    def _draw_squares(self):
        board_rect = self.screen_context.get_board_rect()
        square_width = board_rect.width // self.board_size
        square_height = board_rect.height // self.board_size
        for row in range(self.board_size):
            for col in range(self.board_size):
                self._draw_square(row, col, board_rect, square_width, square_height)
                
    def _draw_square(self, row:int, col:int, board_rect:pygame.Rect, square_width:int, square_height:int):
        square_rect = pygame.Rect(
            board_rect.left + col * square_width,
            board_rect.top + row * square_height,
            square_width,
            square_height
        )
        square_color = SQUARE_COLOR_1 if (row + col) % 2 == 0 else SQUARE_COLOR_2
        pygame.draw.rect(self.screen_context.get_window(), square_color, square_rect)
                
    def _draw_pieces(self):
        board_rect = self.screen_context.get_board_rect()
        square_width = board_rect.width // self.board_size
        square_height = board_rect.height // self.board_size
        for row in range(self.board_size):
            for col in range(self.board_size):
                self._draw_piece(row, col, board_rect, square_width, square_height)
                
    def _draw_piece(self, row:int, col:int, board_rect:pygame.Rect, square_width:int, square_height:int):
        piece = self.board[row][col]
        # if piece == None:
        #     return
        # if piece.side == PieceSide.PLAYER:
        #     piece_color = PLAYER_PIECE_COLOR if not piece.king else PLAYER_KING_COLOR
        # elif piece.side == PieceSide.COMPUTER:
        #     piece_color = OPPONENT_PIECE_COLOR if not piece.king else OPPONENT_KING_COLOR
            
        # piece_rect = pygame.Rect(
        #     board_rect.left + col * square_width,
        #     board_rect.top + row * square_height,
        #     square_width,
        #     square_height
        # )
        
        # pygame.draw.circle(self.screen_context.get_window(), piece_color, piece_rect.center, square_width // 2 - 10)
        
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
        board_rect = self.screen_context.get_board_rect()
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