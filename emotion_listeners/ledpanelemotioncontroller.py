#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import time
from typing import Dict, Any
from emotions import Emotion
from emotioncolors import EmotionColors
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from zmq_server_controllers import BaseZMQListener

DEFAULT_ZMQ_ADDRESS = "tcp://localhost:5555"
DEFAULT_BRIGHTNESS = 100
DEFAULT_MATRIX_ROWS = 64
DEFAULT_MATRIX_COLS = 64


class LEDPanelEmotionController(BaseZMQListener):
    """
    Derived class for handling LED panel-related payloads via ZMQ listener.
    """

    def __init__(self, address: str = DEFAULT_ZMQ_ADDRESS):
        super().__init__(address)
        self.matrix = self.initialize_led_matrix()
        self.canvas = self.matrix.CreateFrameCanvas()
        self.canvas_dimensions = self.calculate_drawable_area("25%", "10%", "10%", "10%")

    @staticmethod
    def initialize_led_matrix() -> RGBMatrix:
        """Configure and return the LED matrix."""
        options = RGBMatrixOptions()
        options.hardware_mapping = "regular"
        options.rows = DEFAULT_MATRIX_ROWS
        options.cols = DEFAULT_MATRIX_COLS
        options.chain_length = 1
        options.parallel = 1
        options.pwm_bits = 11
        options.brightness = DEFAULT_BRIGHTNESS
        options.led_rgb_sequence = "RGB"
        options.scan_mode = 1
        return RGBMatrix(options=options)

    def calculate_drawable_area(self, top="50%", bottom="50%", left="50%", right="50%") -> Dict[str, Dict[str, int]]:
        """
        Calculate the drawable area on the canvas based on margin percentages or pixel values.
        """
        top_px = self._parse_dimension(top, self.canvas_height)
        bottom_px = self._parse_dimension(bottom, self.canvas_height)
        left_px = self._parse_dimension(left, self.canvas_width)
        right_px = self._parse_dimension(right, self.canvas_width)
        self._validate_dimensions(top_px, bottom_px, left_px, right_px)
        return {
            'top': {'x_start': 0, 'x_end': self.canvas_width, 'y_start': 0, 'y_end': top_px},
            'bottom': {'x_start': 0, 'x_end': self.canvas_width, 'y_start': self.canvas_height - bottom_px,
                       'y_end': self.canvas_height},
            'left': {'x_start': 0, 'x_end': left_px, 'y_start': top_px, 'y_end': self.canvas_height - bottom_px},
            'right': {'x_start': self.canvas_width - right_px, 'x_end': self.canvas_width, 'y_start': top_px,
                      'y_end': self.canvas_height - bottom_px},
        }

    @staticmethod
    def _parse_dimension(dimension: str, max_value: int) -> int:
        """Convert dimension string (e.g., '10%' or '25px') into pixel value."""
        if dimension.endswith("px"):
            return int(dimension[:-2])
        elif dimension.endswith("%"):
            return math.ceil(float(dimension[:-1]) / 100 * max_value)
        else:
            raise ValueError(f"Invalid dimension format: {dimension}")

    def _validate_dimensions(self, top_px: int, bottom_px: int, left_px: int, right_px: int):
        """Ensure the drawable area dimensions are within valid bounds."""
        if top_px + bottom_px > self.canvas_height or left_px + right_px > self.canvas_width:
            raise ValueError("Invalid dimensions: excluded areas exceed the max dimensions.")

    def process(self, message: Dict[str, Any]):
        """Process LED panel-related payloads."""
        if message.get("action") == "draw":
            try:
                emotion = Emotion(message.get("emotion"))
                self.logger.info(f"Drawing emotion: {emotion}")
                self._draw_on_led(emotion)
            except ValueError as e:
                self.logger.debug(f"Invalid emotion: {e}")

    def _draw_on_led(self, emotion: Emotion):
        """Send emotion color to the canvas and refresh."""
        rgba = EmotionColors.color_provider(emotion)
        time.sleep(0.005)  # reduce brightness flicker
        self._fill_canvas(*rgba)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def _fill_canvas(self, red: int, green: int, blue: int, brightness: int = DEFAULT_BRIGHTNESS):
        """Fill the canvas with a given color."""
        self.canvas.brightness = brightness
        if brightness <= 0:  # No need to draw if brightness is zero
            return
        # Check for complete fill condition
        total_fillable_height = self.canvas_dimensions['top']['y_end'] + \
                                (self.canvas_height - self.canvas_dimensions['bottom']['y_start'])
        total_fillable_width = self.canvas_dimensions['left']['x_end'] + \
                               (self.canvas_width - self.canvas_dimensions['right']['x_start'])
        if total_fillable_height >= self.canvas_height or total_fillable_width >= self.canvas_width:
            self.canvas.Fill(red, green, blue)
            return
        # Partial area rendering
        for side, dimensions in self.canvas_dimensions.items():
            for x in range(dimensions['x_start'], dimensions['x_end'] + 1):
                for y in range(dimensions['y_start'], dimensions['y_end'] + 1):
                    self.canvas.SetPixel(x, y, red, green, blue)

    @property
    def canvas_width(self) -> int:
        """Return canvas width."""
        return self.canvas.width

    @property
    def canvas_height(self) -> int:
        """Return canvas height."""
        return self.canvas.height


if __name__ == "__main__":
    emotion_controller = LEDPanelEmotionController()
    emotion_controller.start()
    # Keep the application running
    input("Press Enter to exit...\n")
