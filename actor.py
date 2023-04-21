from typing import Mapping, Optional, Type
import pygame

from base import ICamera, IComponent, IDrawAbleComponent


class Actor:
    def __init__(self, *, position: pygame.Vector2 = pygame.Vector2(0, 0)) -> None:
        self._position = position
        self._component_mapping: Mapping[Type[IComponent], IComponent] = {}
    
    def add_component(self, component: IComponent):
        component_type = type(component)
        if component_type in self._component_mapping:
            raise ValueError
        component.owner = self
        self._component_mapping[type(component)] = component
    
    def get_component(self, component_type: Type[IComponent]) -> Optional[IComponent]:
        return self._component_mapping.get(component_type)
    
    def remove_component(self, component_type: Type[IComponent]):
        del self._component_mapping[component_type]
    
    @property
    def position(self) -> pygame.Vector2:
        return self._position
    
    def update(self, delta_time_ms: int):
        for component in self._component_mapping.values():
            component.update(delta_time_ms)
    
    def draw(self, surface: pygame.Surface, camera: ICamera):
        for component in self._component_mapping.values():
            if isinstance(component, IDrawAbleComponent):
                component.draw(surface, camera)
    