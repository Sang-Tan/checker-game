from abc import ABC, abstractmethod
import pygame

class GameObject(ABC):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def update(self, events: list[pygame.event.Event] = []):
        pass    
    
class VisibleGameObject(GameObject):
    def __init__(self, pos_x:int, pos_y:int, width:int, height:int):
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        super().__init__()
    
    def _get_local_mouse_pos(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self._to_local_pos(mouse_x, mouse_y)
    
    def _to_global_pos(self, x:int, y:int):
        return x + self.rect.left, y + self.rect.top
    
    def _to_local_pos(self, x:int, y:int):
        return x - self.rect.left, y - self.rect.top