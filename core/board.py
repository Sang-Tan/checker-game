import logging
from copy import deepcopy
from .piece import Piece, PieceSide
from .game_state import GameState
from abc import ABC, abstractmethod
from collections import deque

logger = logging.getLogger(__name__)

class BoardData:
    @abstractmethod
    def __getitem__(self, key: int)->list[Piece | None]:
        pass
    
    @abstractmethod
    def get_size(self)->int:
        pass

class PieceMove:
    def __init__(self, row:int, col:int, jump_over: Piece|None = None, before: 'PieceMove | None' = None): # type: ignore
        self.row = row
        self.col = col
        self.jump_over = jump_over
        self.before = before
        self.after:list[PieceMove] = []
        
class Board(GameState, BoardData):
    def __init__(self, total_rows:int, total_cols:int):
        self.board: list[list[Piece | None]] = []
        self.pieces_left = {PieceSide.PLAYER: 12, PieceSide.COMPUTER: 12}
        self.kings = {PieceSide.PLAYER: 0, PieceSide.COMPUTER: 0}
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.create_board()

    def __getitem__(self, key: int)->list[Piece | None]:
        return self.board[key]
    
    def get_size(self)->int:
        return len(self.board)

    def heuristic(self):
        return self.pieces_left[PieceSide.COMPUTER] - self.pieces_left[PieceSide.PLAYER] + \
            (self.kings[PieceSide.COMPUTER] - self.kings[PieceSide.PLAYER])

    def get_all_moves(self, side)->list["Board"]:
        moves = []
        for piece in self.get_pieces_by_side(side):
            valid_moves = self.get_valid_moves(piece)
            for move, skip in valid_moves.items():
                temp_board = deepcopy(self)
                temp_piece = temp_board.get_piece(piece.row, piece.col)
                new_board = temp_board.simulate_move(temp_piece, move, skip)
                moves.append(new_board)
        
        return moves
    
    def get_all_moves_with_nodes(self, side: PieceSide)->list[tuple[PieceMove, "Board"]]:
        ret = []
        # logger.debug(f"Getting all moves for {side}")
        
        # using dfs to get all the possible moves
        # TODO: optimize this
        for piece in self.get_pieces_by_side(side):
            # logger.debug(f"Piece: {piece.row}, {piece.col}")
            move_root = self._get_valid_moves_root(piece)
            
            for move in self._get_all_moves_from_root(move_root):
                
                
                new_board = self.get_state_from_move(move)
                ret.append((move, new_board))
            
        return ret
    
    def get_state_from_move(self, move: PieceMove)->"Board":
        """
        move: last piece move node
        """
        if not move:
            raise Exception("Move is None")
        
        skip:list[Piece] = []
        move_it = move
        while move_it:
            if move_it.jump_over:
                skip.append(move_it.jump_over)
            
            if move_it.before:
                move_it = move_it.before
            else:
                break
            
        first_piece = self.get_piece(move_it.row, move_it.col)
        if not first_piece:
            raise Exception(f'Piece not found at {move_it.row}, {move_it.col}')
            
        temp_board = deepcopy(self)
        temp_piece = temp_board.get_piece(first_piece.row, first_piece.col)
        new_board = temp_board.simulate_move(temp_piece, (move.row, move.col), skip)        
            
        return new_board
        
    def simulate_move(self, piece, move:tuple[int, int], skip:list[Piece]):
        self.move(piece, move[0], move[1])
        if skip:
            self.remove(skip)

        return self

    def get_pieces_by_side(self, side: PieceSide)->list[Piece]:
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

    def get_piece(self, row, col)->Piece | None:
        return self.board[row][col]

    def create_board(self):
        for row in range(self.total_rows):
            self.board.append([])
            for col in range(self.total_cols):
                if col % 2 == ((row +  1) % 2):
                    if row < self.total_rows // 2 - 1:
                        self.board[row].append(Piece(row, col, PieceSide.COMPUTER))
                    elif row > self.total_rows // 2:
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
        move_root = self._get_valid_moves_root(piece)
        moves = move_root.after
    
        ret = {}
        for move in moves:
            for key, value in self._flatten_move(move).items():
                ret[key] = value
            
        # logger.debug(f"Valid moves: {ret}")
                    
        return ret
    
    def _get_valid_moves_root(self, piece: Piece)->PieceMove:
        row = piece.row
        col = piece.col

        root = PieceMove(row, col)
        if piece.side == PieceSide.PLAYER or piece.king:
            # moves.update(self._traverse_left(row -1, max(row-3, -1), -1, piece.side, left))
            # moves.update(self._traverse_right(row -1, max(row-3, -1), -1, piece.side, right))
            left = self._move(row, col, True, True, piece.side)
            right = self._move(row, col, False, True, piece.side)
            
            if left:
                left.before = root
                root.after.append(left)
            if right:
                right.before = root
                root.after.append(right)
        if piece.side == PieceSide.COMPUTER or piece.king:
            # moves.update(self._traverse_left(row +1, min(row+3, self.total_rows), 1, piece.side, left))
            # moves.update(self._traverse_right(row +1, min(row+3, self.total_rows), 1, piece.side, right))
            left = self._move(row, col, True, False, piece.side)
            right = self._move(row, col, False, False, piece.side)
            
            if left:
                left.before = root
                root.after.append(left)
            if right:
                right.before = root
                root.after.append(right)
                
        return root

    def get_all_pieces(self)->list[list[Piece | None]]:
        return self.board
    
    def _flatten_move(self, move: PieceMove)->dict[tuple[int, int], list[Piece]]:
        moves:dict[tuple[int, int], list[Piece]] = {}
        frontier = deque([move])
        
        while len(frontier) > 0:
            current = frontier.popleft()
            before = current.before
            before_jump_all = [] if (before == None or (before.row, before.col) not in moves) else moves[(before.row, before.col)]
            moves[(current.row, current.col)] = before_jump_all + [current.jump_over] if current.jump_over else before_jump_all
            for after in current.after:
                frontier.append(after)
        
        return moves
    
    def _get_all_moves_from_root(self, root: PieceMove)->list[PieceMove]:
        """
        return all the moves from the root node excluding the root node
        """
        moves = []
        frontier = deque([root])
        
        while len(frontier) > 0:
            current = frontier.popleft()
            if current != root:
                moves.append(current)
                
            for after in current.after:
                frontier.append(after)

        return moves
    
    def _move(self, start_row: int, start_col: int, left: bool, up: bool, side: PieceSide, before: PieceMove|None=None)->PieceMove|None:            
        coors_to_check:list[tuple[int, int]] = []
        horizontal = -1 if left else 1
        vertical = -1 if up else 1
        
        for i in range(1, 3):
            cur_row = start_row + i * vertical
            cur_col = start_col + i * horizontal
            if cur_row < 0 or cur_row >= self.total_rows or cur_col < 0 or cur_col >= self.total_cols:
                break
            
            coors_to_check.append((cur_row, cur_col))
            
        last = None
        for coor in coors_to_check:
            cur_row, cur_col = coor
            current = self.board[cur_row][cur_col]
            if current == None:
                if before and not last:
                    return None
                
                if last:
                    move = PieceMove(cur_row, cur_col, jump_over=last, before=before)
                    
                    # if before:
                    #     log_path = []
                    #     while before:
                    #         log_path.append((before.row, before.col))
                    #         before = before.before
                            
                    #     log_path.reverse()
                    #     log_path.append((cur_row, cur_col))
                    #     logger.debug(f"Path: {log_path}")
                    left_move = self._move(cur_row, cur_col, True, up, side, before=move)
                    right_move = self._move(cur_row, cur_col, False, up, side, before=move)
                    if left_move:
                        move.after.append(left_move)
                    if right_move:
                        move.after.append(right_move)
                    return move
                else:
                    return PieceMove(cur_row, cur_col, before=before)
            elif current.side == side:
                return None
            else:
                last = current
                
        return None

    # def _traverse_left(self, start_row: int, stop_row: int, row_step: int, side:PieceSide, cur_col: int, skipped: list[Piece]=[])->list[PieceMove]:
    #     """
    #     skipped:  list of pieces that have been jumped over
    #     """
    #     moves = []
    #     last = []
    #     for cur_row in range(start_row, stop_row, row_step):
    #         if cur_col < 0:
    #             break
            
    #         current = self.board[cur_row][cur_col]
            
    #         # if the adj cell is empty
    #         if current == None:
    #             # if there are pieces that have been jumped over and the last piece has been reached
    #             if skipped and not last:
    #                 break
    #             elif skipped:
    #                 moves[(cur_row, cur_col)] = last + skipped
    #             else:
    #                 moves[(cur_row, cur_col)] = last
                
    #             # jump over the piece
    #             if last:
    #                 if row_step == -1:
    #                     next_stop_row = max(cur_row-3, 0)
    #                 else:
    #                     next_stop_row = min(cur_row+3, self.total_rows)
    #                 moves.update(self._traverse_left(cur_row+row_step, next_stop_row, row_step, side, cur_col-1,skipped=last))
    #                 moves.update(self._traverse_right(cur_row+row_step, next_stop_row, row_step, side, cur_col+1,skipped=last))
    #             break
    #         # if the adj cell has a piece of the current player
    #         elif current.side == side:
    #             break
    #         else:
    #             last = [current]

    #         cur_col -= 1
        
    #     return moves

    # def _traverse_right(self, start_row: int, stop_row: int, row_step: int, side:PieceSide, cur_col: int, skipped:list[Piece]=[])->dict[tuple[int, int], list[Piece]]:
    #     moves = {}
    #     last = []
    #     for cur_row in range(start_row, stop_row, row_step):
    #         if cur_col >= self.total_cols:
    #             break
            
    #         current = self.board[cur_row][cur_col]
    #         if current == None:
    #             if skipped and not last:
    #                 break
    #             elif skipped:
    #                 moves[(cur_row, cur_col)] = last + skipped
    #             else:
    #                 moves[(cur_row, cur_col)] = last
                
    #             if last:
    #                 if row_step == -1:
    #                     row = max(cur_row-3, 0)
    #                 else:
    #                     row = min(cur_row+3, self.total_rows)
    #                 moves.update(self._traverse_left(cur_row+row_step, row, row_step, side, cur_col-1,skipped=last))
    #                 moves.update(self._traverse_right(cur_row+row_step, row, row_step, side, cur_col+1,skipped=last))
    #             break
    #         elif current.side == side:
    #             break
    #         else:
    #             last = [current]

    #         cur_col += 1
        
    #     return moves