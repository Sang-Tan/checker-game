from .game_object import VisibleGameObject
from .game_context import GameContext, GameEvent, GameEventType
import pygame
import logging


logger = logging.getLogger(__name__)

PANEL_COLOR = (128, 128, 128)
                    
class MainPanelButton():
    def __init__(self, x:int, y:int, width:int, height:int, color:tuple[int, int, int]=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = ""
        
    def set_text(self, text:str):
        self.text = text
        
    # def draw(self, surface:pygame.Surface):
    #     pygame.draw.rect(surface, self.color, self.rect)
    #     font = pygame.font.Font(None, 36)
    #     text = font.render(self.text, True, (0, 0, 0))
    #     text_rect = text.get_rect()
    #     text_rect.center = (self.rect.left + self.rect.width // 2, self.rect.top + self.rect.height // 2)
    #     surface.blit(text, text_rect)
    def get_surface(self)->pygame.Surface:
        surface = pygame.Surface((self.rect.width, self.rect.height))
        surface.fill(self.color)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.rect.width // 2, self.rect.height // 2)
        surface.blit(text, text_rect)
        
        return surface
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
        self._init_size_change_button()
    
    def update(self, events: list[pygame.event.Event] = []):
        pass
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = self._get_local_mouse_pos()
                logger.debug(f"Mouse clicked at {mouse_x}, {mouse_y}")
                if self.restart_btn.get_rect().collidepoint(mouse_x, mouse_y):
                    logger.debug(f"Restart button clicked {self.restart_btn.get_rect()}")
                    self.game_context.push_event(GameEvent(GameEventType.RESTART))
                elif self.size_up_btn.rect.collidepoint(mouse_x, mouse_y):
                    logger.debug("Size Up button clicked")
                    self.game_context.push_event(GameEvent(GameEventType.CHANGE_SIZE, data=1))
                elif self.size_down_btn.rect.collidepoint(mouse_x, mouse_y):
                    logger.debug("Size Down button clicked")
                    self.game_context.push_event(GameEvent(GameEventType.CHANGE_SIZE, data=-1))
                    
    def draw(self):
        pygame.draw.rect(self.surface, PANEL_COLOR, self.rect)
        
        self.surface.blit(self.restart_btn, self.restart_btn_rect.move(self.rect.left, self.rect.top))   
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
        self.surface.blit(self.size_up_btn.get_surface(), self.size_up_btn.rect.move(self.rect.left, self.rect.top))
        self.surface.blit(self.size_down_btn.get_surface(), self.size_down_btn.rect.move(self.rect.left, self.rect.top))
    
    def _draw_size_text(self):
        font = pygame.font.Font(None, 36)
        text = font.render(self.size_text, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.rect.left + self.rect.width // 2 - 5, self.rect.top + 375)
        self.surface.blit(text, text_rect)
    
    def _draw_turn_text(self):
        font = pygame.font.Font(None, 36)
        text = font.render(self.turn_text, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.rect.left + self.rect.width // 2, self.rect.top + 150)
        self.surface.blit(text, text_rect)     
    
    def _load_buttons_images(self, root_path:str):
        self.restart_btn = pygame.image.load(f"{root_path}/assets/buttons/restart/normal.png")
        self.restart_btn_rect = self.restart_btn.get_rect()
        self.restart_btn_rect.center = (self.rect.width // 2, self.rect.top + 50)
        
    def _init_size_change_button(self):
        self.size_up_btn = MainPanelButton(10, 300, self.rect.width - 20, 50)
        self.size_up_btn.set_text("Size Up")
        
        self.size_down_btn = MainPanelButton(10, 400, self.rect.width - 20, 50)
        self.size_down_btn.set_text("Size Down")