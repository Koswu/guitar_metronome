from typing import Optional, Protocol, Tuple
import numpy as np
import pyaudio
import aubio
from numpy.typing import NDArray


class IOnsetDetector(Protocol):
    def __call__(self, data: np.ndarray) -> bool:
        raise NotImplementedError

    def set_threshold(self, threshold: float) -> None:
        raise NotImplementedError


class IPitchDetector(Protocol):
    def __call__(self, data: NDArray[np.float32]) -> Tuple[float]:
        raise NotImplementedError

    def set_unit(self, unit: str) -> None:
        raise NotImplementedError

    def set_silence(self, silence: float) -> None:
        raise NotImplementedError


class HitCallback(Protocol):
    def __call__(self, pitch: int):
        """
        pitch: 音高 (MIDI 音符编号 0-127  C4 对应 60)
        """
        raise NotImplementedError


class GuitarInput:
    def __init__(self, hit_callback: HitCallback) -> None:
        self._is_recording = False
        self._sample_rate = 44100
        self._buffer_size = 512
        self._hit_callback = hit_callback
        self._inner_pitch_detector: IPitchDetector = aubio.pitch(  # type: ignore
            "default", self._buffer_size, self._buffer_size // 2, self._sample_rate
        )
        self._inner_onset_detector: IOnsetDetector = aubio.onset(  # type: ignore
            "default", self._buffer_size, self._buffer_size // 2, self._sample_rate
        )
        self._inner_onset_detector.set_threshold(0.2)
        self._inner_pitch_detector.set_unit("midi")
        self._inner_pitch_detector.set_silence(-40)
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self._sample_rate,
            input=True,
            input_device_index=0,
            frames_per_buffer=self._buffer_size // 2,
            stream_callback=self._process_audio_callback,
        )

    def _process_audio_callback(
        self, in_data: Optional[bytes], frame_count: int, time_info, status
    ):
        if in_data is None:
            return None, pyaudio.paContinue
        samples = np.frombuffer(in_data, dtype=np.float32)
        [pitch] = self._inner_pitch_detector(samples)
        onset = self._inner_onset_detector(samples)
        if onset:
            self._hit_callback(round(pitch))
        return in_data, pyaudio.paContinue

    def on_destory(self):
        self._is_recording = False
        self._stream.stop_stream()

    def on_setup(self):
        self._recording = True
        self._stream.start_stream()


if __name__ == "__main__":

    def hit(pitch: int):
        print("hit")

    guitar_input = GuitarInput(hit)
    guitar_input.on_setup()
    input("按回车键停止录音...")
    guitar_input.on_destory()
