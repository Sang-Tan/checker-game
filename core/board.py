import pygame
from copy import deepcopy
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE
from .piece import Piece
from .game_state import GameState

class Board(GameState):
    def __init__(self):
        self.board: list[list[Piece | None]] = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()
    
    def draw_squares(self, win:pygame.Surface):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (row*SQUARE_SIZE, col *SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        return self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5)

    def get_all_moves(self, color):
        moves = []
        for piece in self.get_all_pieces(color):
            valid_moves = self.get_valid_moves(piece)
            for move, skip in valid_moves.items():
                temp_board = deepcopy(self)
                temp_piece = temp_board.get_piece(piece.row, piece.col)
                new_board = temp_board.simulate_move(temp_piece, move, skip)
                moves.append(new_board)
        
        return moves
    
    def simulate_move(self, piece, move, skip):
        self.move(piece, move[0], move[1])
        if skip:
            self.remove(skip)
        
        return self

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != None and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece:Piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1 

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row +  1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)
        
    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != None:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = None
            if piece != None:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1
    
    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        
        return None 
    
    def get_valid_moves(self, piece: Piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row -1, max(row-3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row -1, max(row-3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row +1, min(row+3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row +1, min(row+3, ROWS), 1, piece.color, right))
    
        return moves

    def _traverse_left(self, start_row: int, stop_row: int, row_step: int, color, cur_col: int, skipped: list[Piece]=[]):
        """
        skipped: list[Piece] = [] -> list of pieces that have been jumped over
        """
        moves = {}
        last = []
        for cur_row in range(start_row, stop_row, row_step):
            if cur_col < 0:
                break
            
            current = self.board[cur_row][cur_col]
            
            # if the adj cell is empty
            if current == None:
                # if there are pieces that have been jumped over and the last piece has been reached
                if skipped and not last:
                    break
                elif skipped:
                    moves[(cur_row, cur_col)] = last + skipped
                else:
                    moves[(cur_row, cur_col)] = last
                
                # jump over the piece
                if last:
                    if row_step == -1:
                        next_stop_row = max(cur_row-3, 0)
                    else:
                        next_stop_row = min(cur_row+3, ROWS)
                    moves.update(self._traverse_left(cur_row+row_step, next_stop_row, row_step, color, cur_col-1,skipped=last))
                    moves.update(self._traverse_right(cur_row+row_step, next_stop_row, row_step, color, cur_col+1,skipped=last))
                break
            # if the adj cell has a piece of the current player
            elif current.color == color:
                break
            else:
                last = [current]

            cur_col -= 1
        
        return moves

    def _traverse_right(self, start_row: int, stop_row: int, row_step: int, color, cur_col: int, skipped:list[Piece]=[]):
        moves = {}
        last = []
        for cur_row in range(start_row, stop_row, row_step):
            if cur_col >= COLS:
                break
            
            current = self.board[cur_row][cur_col]
            if current == None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(cur_row, cur_col)] = last + skipped
                else:
                    moves[(cur_row, cur_col)] = last
                
                if last:
                    if row_step == -1:
                        row = max(cur_row-3, 0)
                    else:
                        row = min(cur_row+3, ROWS)
                    moves.update(self._traverse_left(cur_row+row_step, row, row_step, color, cur_col-1,skipped=last))
                    moves.update(self._traverse_right(cur_row+row_step, row, row_step, color, cur_col+1,skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            cur_col += 1
        
        return moves