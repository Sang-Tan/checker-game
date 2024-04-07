from core.board import Board
from core.piece import PieceSide
from minimax.algorithm import minimax
import logging
import sys

# log to console
logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)

board = Board(8, 8)

def print_board(board_data):
    print(" ", end=" ")
    for i in range(len(board_data[0])):
        print(i, end=" ")
        
    print()
        
    for idx, row in enumerate(board_data):
        print(idx, end=" ")
        for piece in row:
            if piece != None:
                name = "C" if piece.side == PieceSide.COMPUTER else "P"
                print(name, end=" ")
            else:
                print(" ", end=" ")
        print()
        
    for _ in range(len(board_data[0])):
        print("-", end=" ")
        
    print(f'\nPlayer pieces left: {board.pieces_left[PieceSide.PLAYER]}')
    print(f'Computer pieces left: {board.pieces_left[PieceSide.COMPUTER]}')
    print()

turn = PieceSide.PLAYER
current_piece = None

while True:
    print_board(board.get_data())
    while True:
        piece_row, piece_col = map(int, input("Enter piece's row and col: ").split())
        piece = board.get_piece(piece_row, piece_col)
        if piece == None:
            print("No piece at that location")
        elif piece.side == PieceSide.COMPUTER:
            print("That's the computer's piece")
        else:
            current_piece = piece
            break
        
    moves = board.get_valid_moves(piece)
    valid_moves = list(moves.keys())
    print("Valid moves: ", valid_moves)
    
    if len(valid_moves) == 0:
        print("No valid moves")
        continue
    
    while True:
        move_row, move_col = map(int, input("Enter move's row and col: ").split())
        if (move_row, move_col) in valid_moves:
            board.move(current_piece, move_row, move_col)
            jumped_over_pieces = moves[(move_row, move_col)]
            if jumped_over_pieces:
                board.remove(jumped_over_pieces)
            break
        else:
            print("Invalid move")
            continue
            
    print_board(board.get_data())
    
    if board.winner() != None:
        print("Winner: ", board.winner())
        break
    
    best_move = minimax(board, 4, True)[1]
    
    if isinstance(best_move, Board):
        board = best_move 
    else:
        raise Exception("Invalid move")
    
    print("Computer's moved")
    
    