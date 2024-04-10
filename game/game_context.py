from common.singleton import SingletonMeta
from enum import Enum
from collections import deque
import pygame

class GameEventType(Enum):
    RESTART = 0
    
class GameEvent:
    def __init__(self, event_type:GameEventType):
        self.event_type = event_type
        
    def get_type(self)->GameEventType:
        return self.event_type
    
    def __str__(self):
        return f"GameEvent({self.event_type})"
    
    def __repr__(self):
        return str(self)

class GameContext(metaclass=SingletonMeta):
    def initialize(self, window_width:int, window_height:int, root_path:str):        
        self._window = pygame.display.set_mode((window_width, window_height))
        self._root_path = root_path
        self._event_queue = deque()
        
    def push_event(self, event:GameEvent):
        self._event_queue.append(event)
        
    def pop_event(self)->GameEvent:
        return self._event_queue.popleft()
    
    def has_event(self)->bool:
        return len(self._event_queue) > 0
        
    def get_window(self):
        return self._window
    
    def get_root_path(self)->str:
        return self._root_path