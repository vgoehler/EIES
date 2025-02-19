#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import math
import sys
import time

import zmq

from emotions import Emotion
from emotioncolors import EmotionColors

from rgbmatrix import RGBMatrix, RGBMatrixOptions

class LEDPanelEmotionController(object):
    def __init__(self, loglevel=logging.INFO):
        self.canvas_dimensions = None
        self.matrix = None
        self.canvas = None
        
        # Initialize logger
        logging.basicConfig(
            level=loglevel,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        self.logger = logging.getLogger("LED_Controller")

    def usleep(self, value):
        time.sleep(value / 1000000.0)

    def define_canvas(self, top="50%", bottom="50%", left="50%", right="50%"):
        """
        Define the drawable Area for fills.
        :return: dict of tuple pixel ranges width:height
        """
        def parse_dimension(dimension, max_value):
            """
            Parse a dimension string (e.g., '45px' or '10%') and calculate the pixel value.

            :param dimension: Dimension string (e.g., '45px', '10%').
            :param max_value: Maximum value for percentage calculations.
            :return: Pixel value as an integer.
            """
            if dimension.endswith("px"):
                return int(dimension[:-2])
            elif dimension.endswith("%"):
                return math.ceil(float(dimension[:-1]) / 100 * max_value)
            else:
                raise ValueError(f"Invalid dimension format: {dimension}")

        top_px = parse_dimension(top, self.canvas.height)
        bottom_px = parse_dimension(bottom, self.canvas.height)
        left_px = parse_dimension(left, self.canvas.width)
        right_px = parse_dimension(right, self.canvas.width)

        # Validate dimensions
        if top_px + bottom_px > self.canvas.height or left_px + right_px > self.canvas.width:
            raise ValueError("Invalid dimensions: excluded areas exceed the max dimensions.")

        return {
            'top': {'x_start': 0, 'x_end': self.canvas.width, 'y_start': 0, 'y_end': top_px},
            'bottom': {'x_start': 0, 'x_end': self.canvas.width, 'y_start': self.canvas.height - bottom_px, 'y_end': self.canvas.height},
            'left': {'x_start': 0, 'x_end': left_px, 'y_start': top_px, 'y_end': self.canvas.height - bottom_px},
            'right': {'x_start': self.canvas.width - right_px, 'x_end': self.canvas.width, 'y_start': top_px, 'y_end': self.canvas.height - bottom_px},
        }

    def run(self):
        self.canvas = self.matrix.CreateFrameCanvas()

        # define drawable area
        self.canvas_dimensions = self.define_canvas("25%", "10%", "10%", "10%")

        context = zmq.Context()
        with context.socket(zmq.SUB) as socket:
            socket.connect("tcp://localhost:5555")
            socket.setsockopt_string(zmq.SUBSCRIBE, "")
            self.logger.info("LED Panel Controller: Waiting for messages...")
            
            # fill drawable area with color according to emotion
            while True:
                message = socket.recv_string()
                self.logger.info(f"LED Panel Controller: Received message: {message}")
                try:
                    emotion = Emotion(message)
                    rgba = EmotionColors.color_provider(emotion)
                except ValueError as e:
                    self.logger.debug(e)
                # draw
                self.usleep(5 * 1000)
                self.draw_on_canvas(*rgba)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
            
    def draw_on_canvas(self, red: int, green: int, blue: int, brightness: int=100):
        """
        This method draws all pixels in the defined canvas in the given color
        :param red: the red color value
        :param green: the green color value
        :param blue: the blue color value
        :param brightness: a percentage of brightness
        :return:
        """
        # set brightness
        self.canvas.brightness = brightness
        # if brightness is 0 then we don't have to do anything
        if brightness <= 0:
            return

        # check for possible fills
        # for top and bottom: if both y areas are bigger than dimension; top y_start is always 0
        if self.canvas_dimensions['top']['y_end'] +1 + \
                self.canvas_dimensions['bottom']['y_end'] +1 - self.canvas_dimensions['bottom']['y_start'] \
                >= self.canvas.height\
                or \
                self.canvas_dimensions['left']['x_end'] +1 - self.canvas_dimensions['left']['x_start'] + \
                self.canvas_dimensions['right']['x_end'] +1 - self.canvas_dimensions['right']['x_start'] \
                >= self.canvas.width:
            # if a fill is detected, just perform the fill and return
            self.canvas.Fill(red, green, blue)
            return

        # draw! loop for top, bottom, left, right
        for side in self.canvas_dimensions.keys():
            if self.canvas_dimensions[side]['x_start'] == self.canvas_dimensions[side]['x_end'] or \
                self.canvas_dimensions[side]['y_end'] == self.canvas_dimensions[side]['y_start']:
                # in case we need not draw anything, just don't draw
                continue
            # start drawing, compensate +1 for range end
            for top_x in range(self.canvas_dimensions[side]['x_start'], self.canvas_dimensions[side]['x_end']+1):
                for top_y in range(self.canvas_dimensions[side]['y_start'], self.canvas_dimensions[side]['y_end']+1):
                    self.canvas.SetPixel(top_x,top_y, red, green, blue)

    def process(self):
        options = RGBMatrixOptions()

        options.hardware_mapping = "regular"
        options.rows = 64
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = 100
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = "RGB"
        options.pixel_mapper_config = ""
        options.panel_type = ""
        options.scan_mode = 1

        self.matrix = RGBMatrix(options=options)

        try:
            # Start loop
            print("Press CTRL-C to stop sample")
            self.run()
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

        return True


# Main function
if __name__ == "__main__":
    emotion_controller = LEDPanelEmotionController()
    emotion_controller.process()
