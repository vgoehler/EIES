import threading
from typing import Dict, Any

from emotions import Emotion
from emotionsounds import EmotionSounds
from zmq_server_controllers import BaseZMQListener

from pydub import AudioSegment
from pydub.playback import play

DEFAULT_FADE_TIME = 1000

DEFAULT_DURATION = 10

DEFAULT_ZMQ_ADDRESS = "tcp://localhost:5555"

class SoundListenerController(BaseZMQListener):
    """
    Derived class for handling sound-related payloads via ZMQ server.
    """

    def __init__(self, address: str = DEFAULT_ZMQ_ADDRESS):
        super().__init__(address)

    def process(self, message: Dict[str, Any]):
        """
        Process sound-related payloads.
        Expected payload format: {"action": "play", "emotion": "...", "duration": 10, "fade_time": 1000}
        :param message: Incoming message
        :return: Response
        """
        if message.get("action") == "play":
            try:
                emotion = Emotion(message.get("emotion"))
                duration = message.get("duration", DEFAULT_DURATION)
                fade_time = message.get("fade_time", DEFAULT_FADE_TIME)
                self.logger.info(f"Playing sound for emotion: {emotion}, for {duration}s with fade time {fade_time}ms")
                filename = EmotionSounds.sound_provider(emotion)
                threading.Thread(target=self._play_audio, args=(filename, duration, fade_time), daemon=True).start()
            except ValueError as e:
                self.logger.debug(f"Invalid emotion: {e}")

    def _play_audio(self, filename: str, duration: int, fade_time: int):
        self.logger.info(f"Playing audio file: {filename}")
        sound = AudioSegment.from_file(filename)

        # Normalize volume
        sound = sound.apply_gain(-sound.max_dBFS)

        # Apply fade-in and fade-out
        sound = sound.fade_in(fade_time).fade_out(fade_time)

        # Calculate how many loops are needed to fill 'duration' seconds
        loops = max(1, duration * 1000 // len(sound))

        # Repeat sound to fill full duration
        full_sound = sound * loops
        full_sound = full_sound[:duration * 1000]  # Trim if slightly over

        play(full_sound)

    def _safeguard_non_negative_int(self, number: int):
        try:
            int_nr = int(number)
            if int_nr < 0:
                raise ValueError("Number must be non-negative")
            return int_nr
        except (ValueError, TypeError):
            self.logger.error(f"Invalid number: {number}")
            return None

    def _validate_duration(self, duration: int):
        dur = self._safeguard_non_negative_int(duration)
        if not dur:
            return DEFAULT_DURATION
        else:
            return dur

    def _validate_fade_time(self, fade_time: int, duration: int):
        ft = self._safeguard_non_negative_int(fade_time)
        if not ft:
            return DEFAULT_FADE_TIME
        else:
            if ft > duration * 500:
                self.logger.warning(f"Fade time ({ft} ms) is longer than half of duration ({duration} sec).")
                return DEFAULT_FADE_TIME
            else:
                return ft

if __name__ == "__main__":
    sound_server = SoundListenerController()
    sound_server.start()
    # Keep the application running
    input("Press Enter to exit...\n")
