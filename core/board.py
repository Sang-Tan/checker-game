import pygame
from copy import deepcopy
from .piece import Piece, PieceSide
from .game_state import GameState

class Board(GameState):
    def __init__(self, total_rows:int, total_cols:int):
        self.board: list[list[Piece | None]] = []
        self.pieces_left = {PieceSide.PLAYER: 12, PieceSide.COMPUTER: 12}
        self.kings = {PieceSide.PLAYER: 0, PieceSide.COMPUTER: 0}
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.create_board()

    def evaluate(self):
        return self.pieces_left[PieceSide.PLAYER] - self.pieces_left[PieceSide.COMPUTER] + (self.kings[PieceSide.PLAYER] - self.kings[PieceSide.COMPUTER])

    def get_all_moves(self, color)->list["Board"]:
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

    def get_all_pieces(self, side: PieceSide)->list[Piece]:
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != None and piece.side == side:
                    pieces.append(piece)
        return pieces

    def move(self, piece:Piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == self.total_rows - 1 or row == 0:
            piece.make_king()
            self.kings[piece.side] += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(self.total_rows):
            self.board.append([])
            for col in range(self.total_cols):
                if col % 2 == ((row +  1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, PieceSide.COMPUTER))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, PieceSide.PLAYER))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)
        
    def remove(self, pieces: list[Piece]):
        for piece in pieces:
            self.board[piece.row][piece.col] = None
            if piece != None:
                if piece.side == PieceSide.PLAYER:
                    self.pieces_left[PieceSide.PLAYER] -= 1
                else:
                    self.pieces_left[PieceSide.COMPUTER] -= 1

                if piece.king:
                    if piece.side == PieceSide.PLAYER:
                        self.kings[PieceSide.PLAYER] -= 1
                    else:
                        self.kings[PieceSide.COMPUTER] -= 1
    
    def winner(self):
        if self.pieces_left[PieceSide.PLAYER] <= 0:
            return PieceSide.COMPUTER
        elif self.pieces_left[PieceSide.COMPUTER] <= 0:
            return PieceSide.PLAYER
        else:
            return None 
    
    def get_valid_moves(self, piece: Piece)->dict[tuple[int, int], list[Piece]]:
        """
        returns a dictionary of all the valid moves that the piece can make, 
        with the key being the move: tuple(move_to_row, move_to_col) and the value being the list of pieces that have been jumped over
        """
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.side == PieceSide.PLAYER or piece.king:
            moves.update(self._traverse_left(row -1, max(row-3, -1), -1, piece.side, left))
            moves.update(self._traverse_right(row -1, max(row-3, -1), -1, piece.side, right))
        if piece.side == PieceSide.COMPUTER or piece.king:
            moves.update(self._traverse_left(row +1, min(row+3, self.total_rows), 1, piece.side, left))
            moves.update(self._traverse_right(row +1, min(row+3, self.total_rows), 1, piece.side, right))
    
        return moves

    def get_data(self)->list[list[Piece | None]]:
        return self.board

    def _traverse_left(self, start_row: int, stop_row: int, row_step: int, side:PieceSide, cur_col: int, skipped: list[Piece]=[])->dict[tuple[int, int], list[Piece]]:
        """
        skipped:  list of pieces that have been jumped over
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
                        next_stop_row = min(cur_row+3, self.total_rows)
                    moves.update(self._traverse_left(cur_row+row_step, next_stop_row, row_step, side, cur_col-1,skipped=last))
                    moves.update(self._traverse_right(cur_row+row_step, next_stop_row, row_step, side, cur_col+1,skipped=last))
                break
            # if the adj cell has a piece of the current player
            elif current.side == side:
                break
            else:
                last = [current]

            cur_col -= 1
        
        return moves

    def _traverse_right(self, start_row: int, stop_row: int, row_step: int, side:PieceSide, cur_col: int, skipped:list[Piece]=[])->dict[tuple[int, int], list[Piece]]:
        moves = {}
        last = []
        for cur_row in range(start_row, stop_row, row_step):
            if cur_col >= self.total_cols:
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
                        row = min(cur_row+3, self.total_rows)
                    moves.update(self._traverse_left(cur_row+row_step, row, row_step, side, cur_col-1,skipped=last))
                    moves.update(self._traverse_right(cur_row+row_step, row, row_step, side, cur_col+1,skipped=last))
                break
            elif current.side == side:
                break
            else:
                last = [current]

            cur_col += 1
        
        return moves