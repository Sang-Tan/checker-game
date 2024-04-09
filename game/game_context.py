import pygame

class GameContext:
    def __init__(self, width:int, height:int, root_path:str):
        self._window = pygame.display.set_mode((width, height))
        self._root_path = root_path
        
    def get_window(self):
        return self._window
    
    def get_board_rect(self)->pygame.Rect:
        return self._window.get_rect()
    
    def get_root_path(self)->str:
        return self._root_path