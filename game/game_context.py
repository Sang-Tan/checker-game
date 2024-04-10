import pygame

class GameContext:
    def __init__(self, window_width:int, window_height:int, root_path:str):        
        self._window = pygame.display.set_mode((window_width, window_height))
        self._root_path = root_path
        
    def get_window(self):
        return self._window
    
    def get_root_path(self)->str:
        return self._root_path