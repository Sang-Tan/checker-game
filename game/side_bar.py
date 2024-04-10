from .game_object import VisibleGameObject
import pygame

class SideBar(VisibleGameObject):
    def __init__(self, pos_x:int, pos_y:int, width:int, height:int):
        super().__init__(pos_x, pos_y, width, height)
        
    def render(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), (self.pos_x, self.pos_y, self.width, self.height))
        
    def update(self):
        pass