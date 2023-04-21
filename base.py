from __future__ import annotations
from typing import Dict, List, Mapping, Optional, Protocol, Tuple, Type, runtime_checkable

import pygame

@runtime_checkable
class Updateable(Protocol):
    def update(self, delta_time_ms: int):
        raise NotImplemented


class ICamera(Updateable, Protocol):
    def world_to_screen(self, world_position: pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(world_position.x - self.get_position().x, world_position.y - self.get_position().y)
    
    def get_horizon_rect_in_world(self) -> pygame.Rect:
        x = self.get_position().x
        y = self.get_position().y 
        return pygame.Rect(x, y, self.get_horizon_size().x,  self.get_horizon_size().y)
    
    def is_rect_visiable(self, rect: pygame.Rect) -> bool:
        return rect.colliderect(self.get_horizon_rect_in_world())
    
    def get_horizon_size(self) -> pygame.Vector2:
        raise NotImplementedError
    
    def get_position(self):
        raise NotImplementedError
    
    def set_position(self, position: pygame.Vector2):
        raise NotImplementedError
    
    def lock_target(self, target: IActor):
        raise NotImplementedError
    
    def unlock_target(self):
        raise NotImplementedError

    def get_target(self) -> Optional[IActor]:
        raise NotImplementedError
    
    def get_target_relative_position(self) -> pygame.Vector2:
        raise NotImplementedError
    
    
    def update(self, delta_time_ms: int):
        target = self.get_target()
        if target is None:
            return
        self.set_position(target.get_position() + self.get_target_relative_position())

@runtime_checkable
class WorldDrawable(Protocol):
    def draw(self, surface: pygame.Surface, camera: ICamera):
        """draw self to surface"""
        pass

@runtime_checkable
class IActor(Updateable, Protocol):
    def update(self, delta_time_ms: int):
        for component in self._get_component_dict().values():
            component.update(delta_time_ms)
    
    def get_position(self) -> pygame.Vector2:
        return pygame.Vector2(0, 0)
    
    def add_component(self, component: IComponent):
        if type(component) in self._get_component_dict():
            raise ValueError
        self._get_component_dict()[type(component)] = component
    
    def get_component(self, component_type: Type[IComponent]) -> Optional[IComponent]:
        return self._get_component_dict().get(component_type, None)
    
    def _get_component_dict(self) -> Dict[Type[IComponent], IComponent]:
        raise NotImplementedError
    
    def draw(self, surface: pygame.Surface, camera: ICamera):
        for component in self._get_component_dict().values():
            if isinstance(component, WorldDrawable):
                component.draw(surface, camera)
    

@runtime_checkable
class EventHandleAble(Protocol):
    def handle_event(self, event: pygame.event.Event):
        raise NotImplementedError
    
class IPawn(IActor, Protocol):
    def get_position(self) -> pygame.Vector2:
        raise NotImplementedError

@runtime_checkable
class IComponent(Updateable, Protocol):
    def get_owner(self) -> IActor:
        raise NotImplementedError
    

