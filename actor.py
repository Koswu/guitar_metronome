import logging
from telnetlib import IAC
from typing import Dict, Mapping, Optional, Type
import pygame
from tomlkit import key

from base import (
    CollisionableActor,
    EventHandleAble,
    IActor,
    IActorCollisionEvent,
    ICamera,
    IComponent,
    IEvent,
    IKeyDownEvent,
    IPawn,
)
from event import (
    EVENT_TYPE,
    KEY_TYPE,
    ActorCreateEvent,
    ActorDestructEvent,
    EventManager,
    GuitarHitEvent,
)


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
            EventManager.post_event(
                ActorCreateEvent(BounsActor, position=pygame.Vector2(500, -100))
            )
            self._ms_after_prev_click = 0
            self._click_sound.play()


class PlayerActor(IPawn, EventHandleAble, CollisionableActor):
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
        logging.info("jumping")
        self._velocity.y = -10
        self._in_air = True

    def _handle_key_down_event(self, event: IKeyDownEvent):
        key_type = event.get_key_type()
        match key_type:
            case KEY_TYPE.SPACE:
                self.jump()
            case _:
                pass

    def _handle_guitar_hit_event(self, event: GuitarHitEvent):
        logging.info("guitar hit")
        self.jump()

    def handle_event(self, event: IEvent):
        if isinstance(event, IKeyDownEvent):
            self._handle_key_down_event(event)
        elif isinstance(event, GuitarHitEvent):
            self._handle_guitar_hit_event(event)

    def update(self, delta_time_ms: int):
        super().update(delta_time_ms)
        t = delta_time_ms
        self._position += self._velocity * t
        self._velocity += self._gravity
        if self._position.y >= 0:
            self._velocity.y = 0
            self._position.y = 0
            self._in_air = False
        elif self._position.y <= -100:
            self._position.y = -100
            self._velocity.y = max(self._velocity.y, 0)

    def get_collision_rect(self) -> pygame.Rect:
        sprite_size = self._sprite.get_size()
        rect = pygame.Rect(
            self._position.x, self._position.y, sprite_size[0], sprite_size[1]
        )
        collision_size = 4
        return pygame.Rect(
            rect.centerx - collision_size // 2,
            rect.top - collision_size + 20,
            collision_size,
            collision_size,
        )

    def draw(self, surface: pygame.Surface, camera: ICamera):
        super().draw(surface, camera)

        if camera.is_rect_visiable(
            self._sprite.get_rect().move(self._position.x, self._position.y)
        ):
            surface.blit(self._sprite, camera.world_to_screen(self._position))


class BounsActor(CollisionableActor, EventHandleAble):
    def __init__(self, position: pygame.Vector2) -> None:
        super().__init__()
        self._position = position
        self._sprite = pygame.image.load("bouns.png")
        self._component_dict: Dict[Type[IComponent], IComponent] = {}
        self._velocity = pygame.Vector2(-0.1, 0)
        self._sound = pygame.mixer.Sound("coin.wav")

    def _get_component_dict(self) -> Dict[Type[IComponent], IComponent]:
        return self._component_dict

    def get_position(self) -> pygame.Vector2:
        return self._position

    def update(self, delta_time_ms: int):
        self._position += self._velocity * delta_time_ms

    def draw(self, surface: pygame.Surface, camera: ICamera):
        super().draw(surface, camera)

        if camera.is_rect_visiable(
            self._sprite.get_rect().move(self._position.x, self._position.y)
        ):
            surface.blit(self._sprite, camera.world_to_screen(self._position))
        else:
            logging.info("cleaning up bouns")
            EventManager.post_event(ActorDestructEvent(self))

    def get_collision_rect(self) -> pygame.Rect:
        sprite_size = self._sprite.get_size()
        rect = pygame.Rect(
            self._position.x, self._position.y, sprite_size[0], sprite_size[1]
        )
        collision_size = 4
        return pygame.Rect(
            rect.centerx - collision_size // 2,
            rect.bottom - collision_size,
            collision_size,
            collision_size,
        )

    def handle_event(self, event: IEvent):
        match event.get_type():
            case EVENT_TYPE.ACTOR_COLLISION:
                assert isinstance(event, IActorCollisionEvent)
                if self not in event.get_actors():
                    return
                self._sound.play()
                EventManager.post_event(ActorDestructEvent(self))
            case _:
                pass
