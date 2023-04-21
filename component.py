
import logging
from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

import pygame


if TYPE_CHECKING:
    from .entry import Actor, Camera



class Component(Protocol):
    owner: Actor

    def update(self, delta_time_ms: int):
        pass

@runtime_checkable
class DrawAbleComponent(Component, Protocol):
    def draw(self, surface: pygame.Surface, camera: Camera):
        """draw self to surface"""
        pass

class MetronomeComponent(Component):
    def __init__(self, bpm: int = 180) -> None:
        super().__init__()
        self.owner: Actor = None
        self._bpm = bpm
        self._ms_after_prev_click = 0
        self._click_sound = pygame.mixer.Sound("metronome.wav")
        self._sec_beat_time = 60 / self._bpm

    def update(self, delta_time_ms: int):
        self._ms_after_prev_click += delta_time_ms
        if self._ms_after_prev_click >= self._sec_beat_time * 1000:
            logging.info("playing click")
            self._ms_after_prev_click = 0
            self._click_sound.play()
    
    def get_owner(self) -> Actor:
        return self._owner


class SpriteComponent(DrawAbleComponent):
    def __init__(self, texture2d: pygame.Surface):
        self._texture2d = texture2d
    
    def update(self, delta_time_ms: int):
        pass

    @property
    def texture2d(self) -> pygame.Surface:
        return self._texture2d
    
    def draw(self, surface: pygame.Surface, camera: Camera):
        if camera.is_rect_visiable(self._texture2d.get_rect().move(self.owner.position.x, self.owner.position.y)):
            surface.blit(self._texture2d, camera.world_to_screen(self.owner.position))
    