import pygame
from enum import Enum

class PieceSide(Enum):
    PLAYER = 1
    COMPUTER = 2

class Piece:
    def __init__(self, row: int, col: int, side: PieceSide):
        self.row = row
        self.col = col
        self.side = side
        self.king = False

    def make_king(self):
        self.king = True

    def move(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return str(self.side)