import logging
from telnetlib import IAC
from typing import Dict, Mapping, Optional, Type
import pygame

from base import EventHandleAble, IActor, ICamera, IComponent, IPawn


class MetronomeActor(IActor):
    def __init__(self, bpm: int = 120):
        self._component_dict: Dict[Type[IComponent], IComponent] = {}
        self._bpm = bpm
        self._ms_after_prev_click = 0
        self._click_sound = pygame.mixer.Sound("metronome.wav")
        self._sec_beat_time = 60 / self._bpm

    def _get_component_dict(self) -> Dict[Type[IComponent], IComponent]:
        return self._component_dict
    
    def update(self, delta_time_ms: int):
        super().update(delta_time_ms)
        self._ms_after_prev_click += delta_time_ms
        if self._ms_after_prev_click >= self._sec_beat_time * 1000:
            logging.info("playing click")
            self._ms_after_prev_click = 0
            self._click_sound.play()


class PlayerActor(IPawn, EventHandleAble):
    def __init__(self) -> None:
        super().__init__()
        self._position = pygame.Vector2(0, 0)
        self._sprite = pygame.image.load("player.png")
        self._component_dict: Dict[Type[IComponent], IComponent] = {}
        self._velocity = pygame.Vector2(0, 0)
        self._gravity = pygame.Vector2(0, 0.1)
        self._in_air = False
    
    def _get_component_dict(self) -> Dict[Type[IComponent], IComponent]:
        return self._component_dict
    
    def get_position(self) -> pygame.Vector2:
        return self._position
    
    def jump(self):
        if self._in_air:
            logging.info("already jumping")
            return
        logging.info("jumping")
        self._velocity.y = -5
        self._in_air = True

    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_SPACE:
            self.jump()
    
    def update(self, delta_time_ms: int):
        super().update(delta_time_ms)
        self._position += self._velocity
        self._velocity += self._gravity
        if self._position.y >= 0:
            self._velocity.y = 0
            self._position.y = 0
            self._in_air = False

    def draw(self, surface: pygame.Surface, camera: ICamera):
        super().draw(surface, camera)
        
        if camera.is_rect_visiable(self._sprite.get_rect().move(self._position.x, self._position.y)):
            surface.blit(self._sprite, camera.world_to_screen(self._position))
    
    
    
    