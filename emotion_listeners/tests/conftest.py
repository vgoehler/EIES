from unittest.mock import MagicMock

import pytest

import ledpanelemotioncontroller
from emotion_listeners.ledpanelemotioncontroller import LEDPanelEmotionController
from soundservercontroller import SoundListenerController
from zmq_server_controllers import BaseZMQListener


class CanvasStub(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

@pytest.fixture
def ledpanel_controller_bare(monkeypatch):
    # Override the __init__ to do nothing
    monkeypatch.setattr(LEDPanelEmotionController, "__init__", lambda self: None)
    instance = LEDPanelEmotionController()
    BaseZMQListener.__init__(instance, ledpanelemotioncontroller.DEFAULT_ZMQ_ADDRESS)

    instance.canvas = CanvasStub(1920, 1080)
    return instance

@pytest.fixture
def controller_instance():
    """Fixture to create an instance of the controller."""
    return SoundListenerController()

@pytest.fixture
def panel(mock_canvas, monkeypatch):
    # Override the __init__ to do nothing
    monkeypatch.setattr(LEDPanelEmotionController, "__init__", lambda self: None)
    panel = LEDPanelEmotionController()
    BaseZMQListener.__init__(panel, ledpanelemotioncontroller.DEFAULT_ZMQ_ADDRESS)

    panel.canvas = mock_canvas
    panel.canvas_dimensions = {
        "top": {"x_start": 0, "x_end": 63, "y_start": 0, "y_end": 20},
        "bottom": {"x_start": 0, "x_end": 63, "y_start": 30, "y_end": 63},
        "left": {"x_start": 0, "x_end": 20, "y_start": 20, "y_end": 30},
        "right": {"x_start": 30, "x_end": 63, "y_start": 20, "y_end": 30}
    }
    # set mock matrix
    mock_matrix = MagicMock()
    mock_matrix.SwapOnVSync = lambda canvas: canvas
    panel.matrix = mock_matrix

    return panel

@pytest.fixture
def mock_canvas():
    canvas_mock = MagicMock()
    canvas_mock.SetPixel = MagicMock()
    canvas_mock.Fill = MagicMock()
    canvas_mock.brightness = 100
    canvas_mock.width = 64
    canvas_mock.height = 64
    return canvas_mock
