from functools import cached_property
import time
import threading
from typing import Callable
import numpy as np
import sounddevice as sd
import aubio
import logging
import pygame

logging.basicConfig(format="%(asctime)s;%(levelname)s;%(message)s", level=logging.INFO)

class Metronome:
    def __init__(self, bpm: int, note_type: str, tolerance: float, error_callback: Callable):
        self.bpm = bpm
        self.note_type = note_type
        self.tolerance = tolerance
        self.error_callback = error_callback
        self.note_duration = self.calculate_note_duration()
        self.audio_data = []
        self.audio_data_lock = threading.Lock()
        self._clock = pygame.time.Clock()

        pygame.mixer.init()

    def calculate_note_duration(self) -> float:
        if self.note_type == "16th":
            return 60 / self.bpm / 4
        elif self.note_type == "8th":
            return 60 / self.bpm / 2
        else:
            raise ValueError(f"Invalid note type: {self.note_type}")
    
    @cached_property
    def _beat_sound(self):
        return pygame.mixer.Sound("metronome.wav")
    
    def _play_metronome_beat(self):
        while True:
            logging.info("playing click")
            self._beat_sound.play()
            self._clock.tick(1/self.note_duration)


    def process_audio(self, indata: np.ndarray, frames: int, time_info, status: sd.CallbackFlags) -> None:
        # logging.info("reading audio")
        with self.audio_data_lock:
            self.audio_data.append(indata[:, 0])


    def start_guitar_input(self) -> None:
        with sd.InputStream(callback=self.process_audio):
            while True:
                sd.sleep(1000)


    def analyze_audio(self) -> None:
        hop_size = 256
        onset_o = aubio.onset("default", hop_size * 4, hop_size, 44100)

        while True:
            time.sleep(self.note_duration)
            with self.audio_data_lock:
                audio_data = np.concatenate(self.audio_data)
                self.audio_data = []
            if len(audio_data) == 0:
                continue

            onsets = []
            for i in range(0, len(audio_data) - hop_size, hop_size):
                chunk = audio_data[i:i + hop_size]
                if onset_o(chunk):
                    onsets.append(i / 44100)

            if len(onsets) > 0:
                nearest_beat = round(time.time() / self.note_duration) * self.note_duration
                error = abs(time.time() - nearest_beat)
                if error > self.tolerance:
                    self.error_callback(error)


    def start(self) -> None:
        metronome_thread = threading.Thread(target=self._play_metronome_beat, daemon=True)
        guitar_input_thread = threading.Thread(target=self.start_guitar_input, daemon=True)
        analyze_audio_thread = threading.Thread(target=self.analyze_audio, daemon=True)

        metronome_thread.start()
        guitar_input_thread.start()
        analyze_audio_thread.start()

        while True:
            time.sleep(1)

def error_callback(error: float) -> None:
    print(f"Timing error: {error:.2f} seconds")

if __name__ == "__main__":
    bpm = 240
    note_type = "8th"
    tolerance = 0.1

    metronome = Metronome(bpm, note_type, tolerance, error_callback)
    metronome.start()

