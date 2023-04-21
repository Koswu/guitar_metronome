from __future__ import annotations
from dataclasses import dataclass
import logging
from typing import List, Mapping, Optional, Protocol, Type, runtime_checkable
from cairo import Surface
import pygame
from pytools import delta

from component import Component, MetronomeComponent, SpriteComponent

logging.basicConfig(format="%(asctime)s;%(levelname)s;%(message)s", level=logging.INFO)

class Game:
    def __init__(self) -> None:
        self._running = True
        self._fps = 60
        self._clock = pygame.time.Clock()
        self._actor_list: List[Actor] = []
        self._screen: pygame.Surface = None
        self._camera: Camera = None

    def _handle_one_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self._running = False
        else:
            pass

    def _handle_event(self):
        for event in pygame.event.get():
            self._handle_one_event(event)
    
    def _update_status(self):
        for actor in self._actor_list:
            actor.update(self._clock.get_time())
    
    def add_actor(self, actor: Actor):
        self._actor_list.append(actor)
    
    def _setup(self):
        pygame.init()
        self._screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Metronome")
        self._screen.fill(pygame.color.Color("white"))  

        self._camera = Camera(self._screen)

        metronome_actor = Actor()
        metronome_actor.add_component(MetronomeComponent())

        player_actor = Actor()
        player_actor.add_component(SpriteComponent(pygame.image.load("player.png")))

        self.add_actor(metronome_actor)
        self.add_actor(player_actor)

    
    def _paint(self):
        self._screen.fill(pygame.color.Color("white"))
        for actor in self._actor_list:
            actor.draw(self._screen, self._camera)
    
    def start(self):
        # pygame.mixer.init(channels=1, frequency=44100, size=-16, buffer=1024)
        self._setup()

        while self._running:
            logging.debug("one loop")
            self._handle_event()
            self._update_status()
            self._clock.tick(self._fps)
            self._paint()
            pygame.display.flip()

        pygame.quit()

class Actor:
    def __init__(self, *, position: pygame.Vector2 = pygame.Vector2(0, 0)) -> None:
        self._position = position
        self._component_mapping: Mapping[Type[Component], Component] = {}
    
    def add_component(self, component: Component):
        component_type = type(component)
        if component_type in self._component_mapping:
            raise ValueError
        component.owner = self
        self._component_mapping[type(component)] = component
    
    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        return self._component_mapping.get(component_type)
    
    def remove_component(self, component_type: Type[Component]):
        del self._component_mapping[component_type]
    
    @property
    def position(self) -> pygame.Vector2:
        return self._position
    
    def update(self, delta_time_ms: int):
        for component in self._component_mapping.values():
            component.update(delta_time_ms)
    
    def draw(self, surface: pygame.Surface, camera: Camera):
        for component in self._component_mapping.values():
            if isinstance(component, DrawAbleComponent):
                component.draw(surface, camera)
    


class Camera:
    def __init__(self, horizon: Surface) -> None:
        super().__init__()
        self._target: Optional[Actor] = None
        self._point_to: pygame.Vector2 = pygame.Vector2(0, 0)
        self._horizon: Surface = horizon
    
    @property
    def _horizon_rect_in_world(self) -> pygame.Rect:
        x = self._point_to.x
        y = self._point_to.y 
        return pygame.Rect(x, y, self._horizon.get_width(),  self._horizon.get_height())

    
    def is_rect_visiable(self, rect: pygame.Rect) -> bool:
        return rect.colliderect(self._horizon_rect_in_world)


    
    def set_target(self, target: Actor):
        self._target = target
    
    def world_to_screen(self, world_position: pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(world_position.x - self._point_to.x, world_position.y - self._point_to.y)
    
    def update(self, ms_after_prev_update: int):
        pass



def main():
    game = Game()
    game.start()

if __name__ == "__main__":
    main()