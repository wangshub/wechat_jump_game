import time
import math
import random

from PIL import Image, ImageDraw

import settings
from connector import Connector
from algos import get_press_time


class AutoBot(Connector):

    def __init__(self, params=settings.get_bot_params()):
        # init connector
        super(AutoBot, self).__init__()

        # init bot
        self.status = True

        # init game
        self.params = params
        self.swipe_x1 = 0;
        self.swipe_y1 = 0;
        self.swipe_x2 = 0;
        self.swipe_y2 = 0;

    def run(self):
        steps = 0

        while (self.status):
            self.connector_screenshot()
            image = Image.open(self.image_dir)

            steps += 1
            coord_y_start_scan = self._get_coord_y_start_scan(image)
            piece_x, piece_y = self._find_piece(image, coord_y_start_scan)
            board_x, board_y = self._find_board(image, piece_x, piece_y)
            print("step: ", steps)
            print("- image: ", image.size)
            print("- coord_y_start_scan: ", coord_y_start_scan)
            print("- piece (x, y): ", piece_x, piece_y)
            print("- board (x, y): ", board_x, board_y)
            if piece_x == 0: 
                print("Game Over.")
                return

            self._set_button_coords(image)           
            press_time = get_press_time(piece_x, piece_y, board_x, board_y, self.params["TIME_COEFF"])
            print("- press time: ", press_time)
            self.connector_taphold(press_time)
            time.sleep(random.uniform(1, 1.1))


    def _get_coord_y_start_scan(self, image):
        width, height = image.size
        pixels = image.load()
        coord_y_start_scan = 0

        for i in range(self.params["COORD_Y_START_SCAN"], height, 50):
            last_pixel = pixels[0, i]
            for j in range(1, width):
                pixel = pixels[j, i]

                if (pixel[0] != last_pixel[0]) or (pixel[1] != last_pixel[1]) or (pixel[2] != last_pixel[2]):
                    coord_y_start_scan = i - 50
                    break;

            if coord_y_start_scan: break;

        return coord_y_start_scan

    def _find_piece(self, image, coord_y_start_scan):
        width, height = image.size
        pixels = image.load()

        border_x_scan = int(width/8)
        piece_x_sum = 0
        piece_x_counter = 0
        piece_y_max = 0

        for i in range(coord_y_start_scan, int(height * 2 / 3)):
            for j in range(border_x_scan, width - border_x_scan):
                pixel = pixels[j, i]
                if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                    piece_x_sum += j
                    piece_x_counter += 1
                    piece_y_max = max(i, piece_y_max)

        if not all((piece_x_sum, piece_x_counter)): return 0, 0
        piece_x = piece_x_sum / piece_x_counter
        piece_y = piece_y_max - self.params["PIECE_BASE_HEIGHT_HALF"]
        return piece_x, piece_y


    def _find_board(self, image, piece_x, piece_y):
        width, height = image.size
        pixels = image.load()

        board_x = 0
        board_y = 0

        for i in range(int(height/3), int(height * 2/3)):
            if board_x or board_y: 
                break;

            board_x_sum = 0
            board_x_counter = 0
            last_pixel = pixels[0, i]
            for j in range(width):
                pixel = pixels[j, i]
                if (abs(j - piece_x) < self.params["PIECE_BODY_WIDTH"]):
                    continue
                if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) > 10:
                    board_x_sum += j
                    board_x_counter += 1

            if board_x_sum:
                board_x = board_x_sum / board_x_counter

        # find the centroid of next board
        board_y = piece_y - abs(board_x - piece_x) * math.sqrt(3) / 3
        if not all ((board_x, board_y)):   
            return 0, 0

        return board_x, board_y

    def _set_button_coords(self, image):
        width, height = image.size
        left = width / 2
        top = 1003 * (height / 1280.0) + 10
        self.swipe_x1, self.swipe_y1, self.swipe_x2, self.swipe_y2 = left, top, left, top
