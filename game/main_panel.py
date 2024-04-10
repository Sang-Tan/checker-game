from .game_object import VisibleGameObject
from .game_context import GameContext, GameEvent, GameEventType
import pygame
import logging


logger = logging.getLogger(__name__)

PANEL_COLOR = (151, 126, 59)
                    
class MainPanel(VisibleGameObject):
    _RESTART_BUTTON_X = 10
    _RESTART_BUTTON_Y = 10
    
    def __init__(self, x:int, y:int, width:int, height:int,):
        super().__init__(x, y, width, height)
        self.game_context = GameContext()
        self.surface = self.game_context.get_window()
        
        self.turn_text = ""
        self.size_text = ""
        
        self._load_buttons_images(self.game_context.get_root_path())
    
    def update(self, events: list[pygame.event.Event] = []):
        pass
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = self._get_local_mouse_pos()
                logger.debug(f"Mouse clicked at {mouse_x}, {mouse_y}")
                logger.debug(f"Restart button rect: {self.restart_btn.get_rect().move(self.rect.left, self.rect.top)}")
                if self.restart_btn_rect.collidepoint(mouse_x, mouse_y):
                    logger.debug(f"Restart button clicked")
                    self.game_context.push_event(GameEvent(GameEventType.RESTART))
                elif self.size_up_btn_rect.collidepoint(mouse_x, mouse_y):
                    logger.debug("Size Up button clicked")
                    self.game_context.push_event(GameEvent(GameEventType.CHANGE_SIZE, data=1))
                elif self.size_down_btn_rect.collidepoint(mouse_x, mouse_y):
                    logger.debug("Size Down button clicked")
                    self.game_context.push_event(GameEvent(GameEventType.CHANGE_SIZE, data=-1))
                    
    def draw(self):
        pygame.draw.rect(self.surface, PANEL_COLOR, self.rect)
        
       
        self._draw_turn_text()
        self._draw_size_text()
        self._draw_buttons()
        
        
    def set_turn_text(self, turn:str):
        self.turn_text = turn
        self.draw()
        
    def set_size_text(self, size:str):
        self.size_text = size
        self.draw()
    
    def _draw_buttons(self):
        self.surface.blit(self.restart_btn, self.restart_btn_rect.move(self.rect.left, self.rect.top))  
        self.surface.blit(self.size_up_btn, self.size_up_btn_rect.move(self.rect.left, self.rect.top))
        self.surface.blit(self.size_down_btn, self.size_down_btn_rect.move(self.rect.left, self.rect.top))
    
    def _draw_size_text(self):
        font = pygame.font.Font(None, 36)
        text = font.render(self.size_text, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.rect.left + self.rect.width // 2 - 5, self.rect.bottom - 100)
        self.surface.blit(text, text_rect)
    
    def _draw_turn_text(self):
        font = pygame.font.Font(None, 36)
        text = font.render(self.turn_text, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.rect.left + self.rect.width // 2, self.rect.top + 50)
        self.surface.blit(text, text_rect)     
    
    def _load_buttons_images(self, root_path:str):
        self.restart_btn = pygame.image.load(f"{root_path}/assets/buttons/restart/normal.png")
        self.restart_btn_rect = self.restart_btn.get_rect()
        self.restart_btn_rect.center = (self.rect.width // 2, self.rect.bottom - 50)
        
        self.size_up_btn = pygame.image.load(f"{root_path}/assets/buttons/size_up/normal.png")
        self.size_up_btn_rect = self.size_up_btn.get_rect()
        self.size_up_btn_rect.center = (self.rect.width // 2, self.rect.bottom - 250)
        
        self.size_down_btn = pygame.image.load(f"{root_path}/assets/buttons/size_down/normal.png")
        self.size_down_btn_rect = self.size_down_btn.get_rect()
        self.size_down_btn_rect.center = (self.rect.width // 2, self.rect.bottom - 190)