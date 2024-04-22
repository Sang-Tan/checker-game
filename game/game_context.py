from common.singleton import SingletonMeta
from enum import Enum
from collections import deque
from typing import Any
import pygame

class GameEventType(Enum):
    RESTART = 0,
    CHANGE_TURN = 1,
    CHANGE_SIZE = 2,
    
class GameEvent:
    def __init__(self, event_type:GameEventType, data:Any = None):
        self._event_type = event_type
        self._data = data
        
    def get_type(self)->GameEventType:
        return self._event_type
    
    def get_data(self)->Any:
        return self._data
    
    def __str__(self):
        return f"GameEvent({self._event_type})"
    
    def __repr__(self):
        return str(self)

class GameContext(metaclass=SingletonMeta):
    def initialize(self, root_path:str, config:dict):      
        window_width = int(config["WINDOW"]["window-width"])
        window_height = int(config["WINDOW"]["window-height"])
        self._window = pygame.display.set_mode((window_width, window_height))
        self._root_path = root_path
        self._event_queue = deque()
        self._config = config
        
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
    
    def get_config(self)->dict:
        if not hasattr(self, "_config"):
            raise Exception("Config not set")
        return self._config