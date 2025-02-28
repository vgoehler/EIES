import threading
import time
from pydub import AudioSegment
from pydub.playback import play

class SoundEngineController(object):
    """
    This class serves as a controller for managing sound-related operations.
    """

    def __init__(self, config=None):
        """
        Initialize the SoundEngineController with an optional configuration.
        :param config: Optional dictionary containing configuration settings
        """
        self.config = config if config is not None else {}


    def play_audio(filename, duration=10, fade_time=1000):  # fade_time in ms
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

        # Play sound in a separate thread
        threading.Thread(target=play, args=(full_sound,), daemon=True).start()

    # Example: Start playing sound non-blocking
    play_audio("your_sound.mp3")
    time.sleep(12)  # Keep the script alive for testing
