
from typing import Protocol, runtime_checkable

import pygame


class IActor(Protocol):
    pass


class IComponent(Protocol):
    owner: IActor

    def update(self, delta_time_ms: int):
        pass

class ICamera(Protocol):

    def is_rect_visiable(self, rect: pygame.Rect) -> bool:
        pass

    def world_to_screen(self, world_position: pygame.Vector2) -> pygame.Vector2:
        pass

    def set_target(self, target: IActor):
        pass

@runtime_checkable
class IDrawAbleComponent(IComponent, Protocol):
    def draw(self, surface: pygame.Surface, camera: ICamera):
        """draw self to surface"""
        pass

