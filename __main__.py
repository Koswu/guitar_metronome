from __future__ import annotations
from dataclasses import dataclass
import itertools
import logging
from typing import (
    Iterator,
    List,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    Type,
    runtime_checkable,
)
import pygame
from actor import BounsActor, MetronomeActor, PlayerActor
from base import (
    CollisionableActor,
    EventHandleAble,
    IActor,
    IActorCollisionEvent,
    ICamera,
    IEvent,
    SingleActorWarpper,
)
from event import EVENT_TYPE, ActorCollisionEvent, EventManager


logging.basicConfig(format="%(asctime)s;%(levelname)s;%(message)s", level=logging.INFO)


class Game:
    def __init__(self) -> None:
        self._running = True
        self._fps = 60
        self._clock = pygame.time.Clock()
        self._actor_list: List[IActor] = []
        self._screen: Optional[pygame.Surface] = None
        self._camera: Optional[Camera] = None

    @property
    def screen(self):
        if self._screen is None:
            raise ValueError
        return self._screen

    @property
    def camera(self):
        if self._camera is None:
            raise ValueError
        return self._camera

    def _handle_one_event(self, event: IEvent):
        match event.get_type():
            case EVENT_TYPE.QUIT:
                self._running = False
            case EVENT_TYPE.ACTOR_DESTRUCT:
                assert isinstance(event, SingleActorWarpper)
                self._actor_list.remove(event.get_actor())
            case _:
                for actor in self._actor_list:
                    if isinstance(actor, EventHandleAble):
                        actor.handle_event(event)

    def _handle_event(self):
        for event in EventManager.get_unhandled_events():
            self._handle_one_event(event)

    def _update_status(self):
        for actor in self._actor_list:
            actor.update(self._clock.get_time())

    def add_actor(self, actor: IActor):
        self._actor_list.append(actor)

    def get_actor(self, actor_type: Type[IActor]):
        return actor_type

    def _setup(self):
        pygame.init()
        self._screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Metronome")
        self._screen.fill(pygame.color.Color("white"))

        self._camera = Camera(
            pygame.Vector2(self._screen.get_size()), pygame.Vector2(0, -200)
        )

        metronome_actor = MetronomeActor()
        player_actor = PlayerActor()
        bouns_actor = BounsActor(pygame.Vector2(0, -100))

        self.add_actor(metronome_actor)
        self.add_actor(player_actor)
        self.add_actor(bouns_actor)

    def _paint(self):
        self.screen.fill(pygame.color.Color("white"))
        for actor in self._actor_list:
            actor.draw(self.screen, self.camera)

    def _process_collision(self):
        collisionable_actors = [
            actor for actor in self._actor_list if isinstance(actor, CollisionableActor)
        ]
        for actor_a, actor_b in itertools.combinations(collisionable_actors, 2):
            if actor_a.get_collision_rect().colliderect(actor_b.get_collision_rect()):
                logging.info("collision")
                EventManager.post_event(ActorCollisionEvent(actor_a, actor_b))

    def start(self):
        # pygame.mixer.init(channels=1, frequency=44100, size=-16, buffer=1024)
        self._setup()

        while self._running:
            logging.debug("one loop")
            self._handle_event()
            self._update_status()
            self._process_collision()
            self._clock.tick(self._fps)
            self._paint()
            pygame.display.flip()

        pygame.quit()


class Camera(ICamera):
    def __init__(self, horizon_size: pygame.Vector2, position: pygame.Vector2) -> None:
        super().__init__()
        self._target: Optional[IActor] = None
        self._target_relative_position = None
        self._position = position
        self._horizon_size = horizon_size

    def get_horizon_size(self) -> pygame.Vector2:
        return self._horizon_size

    def get_position(self):
        return self._position

    def set_position(self, position: pygame.Vector2):
        self._position = position

    def lock_target(self, target: IActor):
        self._target = target

    def unlock_target(self):
        self._target = None

    def get_target(self) -> Optional[IActor]:
        return self._target

    def get_target_relative_position(self) -> pygame.Vector2:
        if self._target_relative_position is None:
            raise ValueError
        return self._target_relative_position


def main():
    game = Game()
    game.start()


if __name__ == "__main__":
    main()
