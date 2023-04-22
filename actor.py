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
from event import EVENT_TYPE, KEY_TYPE, ActorDestructEvent, EventManager


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
        if self._in_air:
            logging.info("already jumping")
            return
        logging.info("jumping")
        self._velocity.y = -5
        self._in_air = True

    def _handle_key_down_event(self, event: IKeyDownEvent):
        key_type = event.get_key_type()
        match key_type:
            case KEY_TYPE.SPACE:
                self.jump()
            case _:
                pass

    def handle_event(self, event: IEvent):
        if isinstance(event, IKeyDownEvent):
            self._handle_key_down_event(event)

    def update(self, delta_time_ms: int):
        super().update(delta_time_ms)
        self._position += self._velocity
        self._velocity += self._gravity
        if self._position.y >= 0:
            self._velocity.y = 0
            self._position.y = 0
            self._in_air = False

    def get_collision_rect(self) -> pygame.Rect:
        return self._sprite.get_rect().move(self._position.x, self._position.y)

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
        self._sound = pygame.mixer.Sound("coin.wav")

    def _get_component_dict(self) -> Dict[Type[IComponent], IComponent]:
        return self._component_dict

    def get_position(self) -> pygame.Vector2:
        return self._position

    def draw(self, surface: pygame.Surface, camera: ICamera):
        super().draw(surface, camera)

        if camera.is_rect_visiable(
            self._sprite.get_rect().move(self._position.x, self._position.y)
        ):
            surface.blit(self._sprite, camera.world_to_screen(self._position))

    def get_collision_rect(self) -> pygame.Rect:
        sprite_size = self._sprite.get_size()
        return pygame.Rect(
            self._position.x, self._position.y, sprite_size[0], sprite_size[1]
        )

    def handle_event(self, event: IEvent):
        match event.get_type():
            case EVENT_TYPE.ACTOR_COLLISION:
                self._sound.play()
                assert isinstance(event, IActorCollisionEvent)
                EventManager.post_event(ActorDestructEvent(self))
            case _:
                pass
