import os.path
import wave
import pytest
from emotionsounds import EmotionSounds
from emotions import Emotion

@pytest.mark.integration
def test_emotion_sounds_files_are_valid_wave():
    """
    Integration test that checks each sound file for existence and verifies
    it is a valid WAV file by attempting to open it with the wave module.
    """
    for emotion in list(Emotion):
        file_path = EmotionSounds.sound_provider(emotion)
        assert os.path.exists(file_path), f"File {file_path} for emotion '{emotion}' does not exist."
        
        try:
            with wave.open(file_path, 'rb') as wav_file:
                # Optionally verify parameters, such as sample width, channels etc.
                assert wav_file.getnchannels() > 0, f"File {file_path} has invalid channel count."
        except wave.Error as e:
            pytest.fail(f"File {file_path} for emotion '{emotion}' is not a valid WAV file: {e}")