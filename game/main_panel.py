from .game_object import VisibleGameObject
from .game_context import GameContext, GameEvent, GameEventType
import pygame
import logging


logger = logging.getLogger(__name__)

PANEL_COLOR = (128, 128, 128)
                    
class MainPanel(VisibleGameObject):
    _RESTART_BUTTON_X = 10
    _RESTART_BUTTON_Y = 10
    
    def __init__(self, x:int, y:int, width:int, height:int,):
        super().__init__(x, y, width, height)
        # self.game_manager = GameManager()
        self.game_context = GameContext()
        self.surface = self.game_context.get_window()
        self._load_buttons_images(self.game_context.get_root_path())
    
    def update(self, events: list[pygame.event.Event] = []):
        pass
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = self._get_local_mouse_pos()
                logger.debug(f"Mouse clicked at {mouse_x}, {mouse_y}")
                if self.restart_btn.get_rect().collidepoint(mouse_x, mouse_y):
                    logger.debug("Restart button clicked")
                    self.game_context.push_event(GameEvent(GameEventType.RESTART))
                    
    def draw(self):
        pygame.draw.rect(self.surface, PANEL_COLOR, self.rect)
        self.surface.blit(self.restart_btn, self.restart_btn_rect)        
        
    def _load_buttons_images(self, root_path:str):
        self.restart_btn = pygame.image.load(f"{root_path}/assets/buttons/restart/normal.png")
        self.restart_btn_rect = self.restart_btn.get_rect()
        self.restart_btn_rect.x = self._RESTART_BUTTON_X + self.rect.x
        self.restart_btn_rect.y = self._RESTART_BUTTON_Y + self.rect.y