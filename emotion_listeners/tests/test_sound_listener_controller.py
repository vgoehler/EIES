import pytest
from unittest.mock import patch, MagicMock, call
from soundservercontroller import SoundListenerController


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


def test_logger_in_process(controller_instance):
    """Test the logger is called during processing."""
    message = {
        "action": "play",
        "emotion": "neutral",
        "duration": 10,
        "fade_time": 1500
    }

    with patch("soundservercontroller.Emotion", return_value="neutral"), \
            patch("soundservercontroller.EmotionSounds.sound_provider", return_value="neutral_sound.mp3"), \
            patch.object(controller_instance.logger, "info") as mock_info_logger:
        # Call method
        controller_instance.process(message)

        # Ensure logger outputs expected details
        mock_info_logger.assert_any_call(
            f"Playing sound for emotion: neutral, for 10s with fade time 1500ms"
        )