import math

def get_press_time(piece_x, piece_y, board_x, board_y, time_coeff):
        distance = math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2)
        press_time = distance * time_coeff / 1000
        return press_time
