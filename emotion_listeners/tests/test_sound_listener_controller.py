from unittest.mock import patch, MagicMock

import pytest

import soundservercontroller


def test_process_valid_payload(controller_instance):
    """Test valid 'play' action payload."""
    valid_message = {
        "action": "play",
        "emotion": "happy",
        "duration": 10,
        "fade_time": 1000
    }

    with patch("soundservercontroller.Emotion") as MockEmotion, \
            patch("soundservercontroller.EmotionSounds.sound_provider", return_value="test_sound.mp3") as mock_provider, \
            patch("soundservercontroller.threading.Thread") as MockThread:
        MockEmotion.return_value = "happy"

        # Call method
        controller_instance.process(valid_message)

        # Check if Emotion was instantiated correctly
        MockEmotion.assert_called_once_with("happy")

        # Check if sound_provider was called
        mock_provider.assert_called_once_with("happy")

        # Check if threading.Thread was started
        MockThread.assert_called_once()
        _, kwargs = MockThread.call_args
        assert kwargs["target"] == controller_instance._play_audio

def test_process_invalid_emotion(controller_instance):
    """Test invalid emotion handling."""
    invalid_message = {
        "action": "play",
        "emotion": "invalid",
        "duration": 10,
        "fade_time": 1000
    }

    with patch("soundservercontroller.Emotion") as MockEmotion:
        # Simulate ValueError raised for invalid emotion
        MockEmotion.side_effect = ValueError("Invalid emotion")

        with patch.object(controller_instance.logger, "debug") as mock_debug_logger:
            # Call method
            controller_instance.process(invalid_message)

            # Verify logger debug message
            mock_debug_logger.assert_called_once_with("Invalid emotion: Invalid emotion")


def test_process_non_play_action(controller_instance):
    """Test process method with non-'play' action."""
    message = {"action": "stop"}

    with patch.object(controller_instance.logger, "info") as mock_info_logger:
        # Call method
        controller_instance.process(message)

        # Ensure no logs related to playing sounds are made
        mock_info_logger.assert_not_called()


def test_play_audio(controller_instance):
    """Test private '_play_audio' method."""
    with patch("soundservercontroller.AudioSegment.from_file") as mock_from_file, \
            patch("soundservercontroller.play") as mock_play:
        # Mock an AudioSegment object
        mock_sound = MagicMock()
        mock_sound.apply_gain.return_value = mock_sound
        mock_sound.fade_in.return_value = mock_sound
        mock_sound.fade_out.return_value = mock_sound
        mock_sound.__len__.return_value = 5000  # 5 seconds

        mock_from_file.return_value = mock_sound

        # Call the private method directly
        controller_instance._play_audio("test_sound.mp3", duration=10, fade_time=1000)

        # Verify file loading
        mock_from_file.assert_called_once_with("test_sound.mp3")

        # Verify sound manipulations
        mock_sound.apply_gain.assert_called_once()
        mock_sound.fade_in.assert_called_once_with(1000)
        mock_sound.fade_out.assert_called_once_with(1000)

        # Verify the playback
        mock_play.assert_called_once()

@pytest.mark.parametrize("input_duration, expected", [
    (15, 15),
    (-15, soundservercontroller.DEFAULT_DURATION),
    ("blah", soundservercontroller.DEFAULT_DURATION),
    (0, soundservercontroller.DEFAULT_DURATION),
    ("16", 16)
])
def test_validate_durations(controller_instance, input_duration, expected):
    result = controller_instance._validate_duration(input_duration)
    assert isinstance(result, int), "Duration should be an integer"
    assert result == expected, f"Expected {expected}, got {result}"

@pytest.mark.parametrize("input_fade_time, duration, expected", [
    (500,10,500),
    (-500,10,soundservercontroller.DEFAULT_FADE_TIME),
    ("blah", 10, soundservercontroller.DEFAULT_FADE_TIME),
    (0, 10, soundservercontroller.DEFAULT_FADE_TIME),
    ("500", 10, 500),
    (5000,10,5000),
    (5001,10,soundservercontroller.DEFAULT_FADE_TIME),
])
def test_validate_fade_time(controller_instance, input_fade_time, duration, expected):
    result = controller_instance._validate_fade_time(input_fade_time, duration)
    assert isinstance(result, int), "Fade time should be an integer"
    assert result == expected, f"Expected {expected}, got {result}"
