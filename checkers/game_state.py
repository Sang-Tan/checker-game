from abc import ABC, abstractmethod

class GameState(ABC):
    @abstractmethod
    def winner(self):
        pass
    
    @abstractmethod
    def evaluate(self):
        pass
    
    @abstractmethod
    def get_all_moves(self, color):
        pass