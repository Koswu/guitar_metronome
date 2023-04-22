from enum import Enum
from telnetlib import IAC
from typing import TYPE_CHECKING, List, Optional, Protocol, Tuple
from django.urls import clear_script_prefix
from matplotlib.pyplot import cla
import pygame

from base import (
    CollisionableActor,
    IActor,
    IActorCollisionEvent,
    IActorDestructEvent,
    IEvent,
    IEventType,
    IKeyDownEvent,
)


class Event(IEvent):
    def __init__(self, event_type: IEventType):
        self._event_type = event_type

    def get_type(self) -> IEventType:
        return self._event_type


class ActorDestructEvent(IActorDestructEvent):
    def __init__(self, actor: IActor):
        self.actor = actor

    def get_actor(self) -> IActor:
        return self.actor

    def get_type(self) -> IEventType:
        return EVENT_TYPE.ACTOR_DESTRUCT


class ActorCollisionEvent(IActorCollisionEvent):
    def __init__(self, first: CollisionableActor, second: CollisionableActor) -> None:
        self._first = first
        self._second = second
        self._collision_rect = self._first.get_collision_rect().clip(
            self._second.get_collision_rect()
        )

    def get_actors(self) -> Tuple[IActor, IActor]:
        return self._first, self._second

    def get_collision_rect(self) -> pygame.Rect:
        return self._collision_rect

    def get_type(self) -> IEventType:
        return EVENT_TYPE.ACTOR_COLLISION


class EVENT_TYPE(Enum):
    QUIT = 1
    ACTOR_DESTRUCT = 2
    ACTOR_COLLISION = 3
    KEY_DOWN = 4

    def get_type_id(self) -> int:
        return self.value

    def get_type_name(self) -> str:
        return self.name


class KEY_TYPE(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SPACE = 5
    OTHER = 100


if TYPE_CHECKING:
    assert issubclass(EVENT_TYPE, IEventType)


class KeyDownEvent(IKeyDownEvent):
    def __init__(self, key_type) -> None:
        self._key_type = key_type

    def get_key_type(self) -> object:
        return self._key_type

    def get_type(self) -> IEventType:
        return EVENT_TYPE.KEY_DOWN


class EventManager:
    @classmethod
    def _convert_keydown_event(cls, event: pygame.event.Event) -> IEvent:
        assert event.type == pygame.KEYDOWN
        match event.key:
            case pygame.K_UP:
                return KeyDownEvent(KEY_TYPE.UP)
            case pygame.K_DOWN:
                return KeyDownEvent(KEY_TYPE.DOWN)
            case pygame.K_LEFT:
                return KeyDownEvent(KEY_TYPE.LEFT)
            case pygame.K_RIGHT:
                return KeyDownEvent(KEY_TYPE.RIGHT)
            case pygame.K_SPACE:
                return KeyDownEvent(KEY_TYPE.SPACE)
            case _:
                return KeyDownEvent(KEY_TYPE.OTHER)

    @classmethod
    def _convert_user_event_to_internal(cls, event: pygame.event.Event) -> IEvent:
        return event.obj

    @classmethod
    def _convert_event_to_internal(cls, event: pygame.event.Event) -> Optional[IEvent]:
        match event.type:
            case pygame.QUIT:
                return Event(EVENT_TYPE.QUIT)
            case pygame.KEYDOWN:
                return cls._convert_keydown_event(event)
            case pygame.USEREVENT:
                return cls._convert_user_event_to_internal(event)
            case _:
                return None

    @classmethod
    def get_unhandled_events(cls) -> List[IEvent]:
        res = pygame.event.get()
        res = [cls._convert_event_to_internal(event) for event in res]
        return [event for event in res if event is not None]

    @classmethod
    def post_event(cls, event: IEvent):
        assert isinstance(event, IEvent)
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, obj=event))
