import pytest
from emotion_listeners.ledpanelemotioncontroller import LEDPanelEmotionController
from soundservercontroller import SoundListenerController


class CanvasStub(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

@pytest.fixture
def emotion_colors_fixture():

    fixture = LEDPanelEmotionController()
    fixture.canvas = CanvasStub(1920, 1080)
    return fixture

@pytest.fixture
def ledpanel_controller_bare(monkeypatch):
    # Override the __init__ to do nothing
    monkeypatch.setattr(LEDPanelEmotionController, "__init__", lambda self: None)
    instance = LEDPanelEmotionController()
    # set members so that we don't get errors in the del
    instance.socket = None
    instance.context = None
    instance.canvas = CanvasStub(1920, 1080)
    return instance

@pytest.fixture
def controller_instance():
    """Fixture to create an instance of the controller."""
    return SoundListenerController()

