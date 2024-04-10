from abc import ABC, abstractmethod
from .piece import PieceSide

class GameState(ABC):
    @abstractmethod
    def winner(self):
        pass
    
    @abstractmethod
    def heuristic(self)->int|float:
        pass
    
    @abstractmethod
    def get_all_moves(self, side:PieceSide)->list["GameState"]:
        pass