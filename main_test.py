from core.board import Board
from core.piece import PieceSide

board = Board(8, 8)

def print_board(board_data):
    for row in board_data:
        for piece in row:
            if piece != None:
                name = "C" if piece.side == PieceSide.COMPUTER else "P"
                print(name, end=" ")
            else:
                print(" ", end=" ")
        print()

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
            break
        
    moves = board.get_valid_moves(piece)
    valid_moves = list(moves.keys())
    print("Valid moves: ", valid_moves)
    