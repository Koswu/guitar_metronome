import pygame
from guitar_input import GuitarInput

pygame.init()
clock = pygame.time.Clock()
metronome_sound = pygame.mixer.Sound("metronome.wav")
started_time = 0
prev_beat_time = 0
prev_note_time = 0
bpm = 180
beat_interval_ms = 60 / bpm * 1000
note_interval_ms = beat_interval_ms / 1
next_note_time = note_interval_ms
is_prev_note_hit = False
is_next_note_hit = False
coin_sound = pygame.mixer.Sound("coin.wav")

hit_time_offset = 0

allowed_error_ms = 30
prefect_ms = 5
good_ms = 10


def hit_callback(pitch: int):
    # TODO: 需要加锁
    global is_prev_note_hit, is_next_note_hit
    hit_time = started_time + clock.get_rawtime() + hit_time_offset
    prev_interval = hit_time - prev_note_time
    next_interval = next_note_time - hit_time
    error = min(prev_interval, next_interval)
    assert prev_interval + next_interval > allowed_error_ms
    if prev_interval < allowed_error_ms:
        if not is_prev_note_hit:
            coin_sound.play()
            print(f"prev, error: {error}")
            is_prev_note_hit = True
        else:
            print(f"repeat, error: {error}")
            return
    elif next_interval < allowed_error_ms:
        is_next_note_hit = True
        coin_sound.play()
        print(f"next, error: {error}")
    else:
        print(f"mid, prev_interval: {prev_interval}, next_interval:  {next_interval}")
        pass


if __name__ == "__main__":
    guitar_input = GuitarInput(hit_callback)
    try:
        while True:
            started_time += clock.get_time()
            clock.tick(120)
            if started_time - prev_beat_time >= beat_interval_ms:
                print("beat")
                metronome_sound.play()
                prev_beat_time = started_time
            if started_time - prev_note_time >= note_interval_ms:
                prev_note_time = started_time
                next_note_time = started_time + note_interval_ms
                if not is_prev_note_hit:
                    print("miss")
                is_prev_note_hit = is_next_note_hit
                is_next_note_hit = False
    except KeyboardInterrupt:
        pygame.quit()
