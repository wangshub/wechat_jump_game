# coding: utf-8
import os
import time
import math
from PIL import Image


def pull_screenshot():
    os.system('~/platform-tools/adb shell screencap -p /sdcard/1.png')
    os.system('~/platform-tools/adb pull /sdcard/1.png .')


def jump(distance):
    press_time = distance * 1.35
    press_time = int(press_time)
    cmd = '~/platform-tools/adb shell input swipe 320 410 320 410 ' + str(press_time)
    print cmd
    os.system(cmd)


def get_pixel_matrix(im):
    pixel_matrix = []
    w, h = im.size
    for i in range(h):
        pixel_line = []
        for j in range(w):
            pixel_line.append(im.getpixel((j, i)))
        pixel_matrix.append(pixel_line)
    return pixel_matrix


def find_piece(pixel_matrix):
    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0

    for i, pixel_line in enumerate(pixel_matrix):
        for j, pixel in enumerate(pixel_line):
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                # print(j, i)
                piece_x_sum += j
                piece_x_c += 1
                piece_y_max = max(i, piece_y_max)
    piece_x = piece_x_sum / piece_x_c
    piece_y = piece_y_max
    # print("=====")
    # print(piece_x, piece_y)
    return piece_x, piece_y - 20


def find_board(pixel_matrix):
    for i, pixel_line in enumerate(pixel_matrix):
        if i < 300:
            continue
        last_pixel = pixel_line[0]
        for j, pixel in enumerate(pixel_line):
            if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) > 10:
                return j, i + 20


def main():
    while True:
        pull_screenshot()
        im = Image.open("./1.png")
        pixel_matrix = get_pixel_matrix(im)
        # 找到下一个 board
        board_x, board_y = find_board(pixel_matrix)
        print(board_x, board_y)
        # 获取棋子位置
        piece_x, piece_y = find_piece(pixel_matrix)
        print(piece_x, piece_y)
        jump(math.sqrt(abs(board_x - piece_x) ** 2 + abs(board_y - piece_y) ** 2))
        time.sleep(2)


if __name__ == '__main__':
    main()
