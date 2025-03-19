import pytest
from emotion_listeners.ledpanelemotioncontroller import LEDPanelEmotionController


@pytest.fixture
def emotion_colors_fixture():
    class CanvasStub(object):
        def __init__(self, width, height):
            self.width = width
            self.height = height

    fixture = LEDPanelEmotionController()
    fixture.canvas = CanvasStub(1920, 1080)
    return fixture

