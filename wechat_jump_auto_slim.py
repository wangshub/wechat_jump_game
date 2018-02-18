#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Erimus'
'''
这个是精简版本，只取x轴距离。
可以适配任意屏幕。
把磁盘读写截图改为内存读写。
可以防止被ban(从抓包数据看没有返回Error)。
'''

import os
import sys
import subprocess
import time
import random
from PIL import Image, ImageDraw
from io import BytesIO

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

screenshot_way = 2


def check_screenshot():  # 检查获取截图的方式
    global screenshot_way
    if (screenshot_way < 0):
        print('暂不支持当前设备')
        sys.exit()
    binary_screenshot = pull_screenshot()
    try:
        Image.open(BytesIO(binary_screenshot)).load()  # 直接使用内存IO
        print('Capture Method: {}'.format(screenshot_way))
    except Exception:
        screenshot_way -= 1
        check_screenshot()


def pull_screenshot():  # 获取截图
    global screenshot_way
    if screenshot_way in [1, 2]:
        process = subprocess.Popen(
            'adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
        screenshot = process.stdout.read()
        if screenshot_way == 2:
            binary_screenshot = screenshot.replace(b'\r\n', b'\n')
        else:
            binary_screenshot = screenshot.replace(b'\r\r\n', b'\n')
        return binary_screenshot
    elif screenshot_way == 0:
        os.system('adb shell screencap -p /sdcard/autojump.png')
        os.system('adb pull /sdcard/autojump.png .')

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def find_piece_and_board(im):  # 寻找起点和终点坐标
    w, h = im.size  # 图片宽高
    im_pixel = im.load()

    def find_piece(pixel):  # 棋子取色精确范围
        return ((40 < pixel[0] < 65) and
                (40 < pixel[1] < 65) and
                (80 < pixel[2] < 105))

    # 寻找棋子 ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

    # 粗查棋子位置
    piece_found, piece_fx, piece_fy = 0, 0, 0
    scan_piece_unit = w // 40  # 间隔单位
    ny = (h + w) // 2  # 寻找下限 从画面中央的正方形的下缘开始
    while ny > (h - w) // 2 and not piece_found:
        ny -= scan_piece_unit
        for nx in range(0, w, scan_piece_unit):
            pixel = im_pixel[nx, ny]
            if find_piece(pixel):
                piece_fx, piece_fy = nx, ny
                piece_found = True
                break
    print('%-12s %s,%s' % ('piece_fuzzy:', piece_fx, piece_fy))
    if not piece_fx:
        return 0, 0  # 没找到棋子

    # 精查棋子位置
    piece_x, piece_x_set = 0, []  # 棋子x/棋子坐标集合
    piece_width = w // 14  # 估算棋子宽度
    piece_height = w // 5  # 估算棋子高度
    for ny in range(piece_fy + scan_piece_unit, piece_fy - piece_height, -4):
        for nx in range(max(piece_fx - piece_width, 0),
                        min(piece_fx + piece_width, w)):
            pixel = im_pixel[nx, ny]
            # print(nx,ny,pixel)
            if find_piece(pixel):
                piece_x_set.append(nx)
        if len(piece_x_set) > 10:
            piece_x = sum(piece_x_set) / len(piece_x_set)
            break
    print('%-12s %s' % ('p_exact_x:', piece_x))

    # 寻找落点 ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆
    board_x = 0
    # 限制棋盘扫描的横坐标 避免音符bug
    if piece_x < w / 2:
        board_x_start, board_x_end = w // 2, w  # 起点和终点的中点是画面中心
    else:
        board_x_start, board_x_end = 0, w // 2

    # 寻找落点顶点
    board_x_set = []  # 目标坐标集合/改为list避免去重
    for by in range((h - w) // 2, (h + w) // 2, 4):
        bg_pixel = im_pixel[0, by]
        for bx in range(board_x_start, board_x_end):
            pixel = im_pixel[bx, by]
            # 修掉脑袋比下一个小格子还高的情况 屏蔽小人左右的范围
            if abs(bx - piece_x) < piece_width:
                continue

            # 修掉圆顶的时候一条线导致的小bug 这个颜色判断应该OK
            if (abs(pixel[0] - bg_pixel[0]) +
                    abs(pixel[1] - bg_pixel[1]) +
                    abs(pixel[2] - bg_pixel[2]) > 10):
                board_x_set.append(bx)

        if len(board_x_set) > 10:
            board_x = sum(board_x_set) / len(board_x_set)
            print('%-12s %s' % ('target_x:', board_x))
            break  # 找到了退出

    return piece_x, board_x

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def set_button_position(im, gameover=0):  # 重设点击位置 再来一局位置
    w, h = im.size
    if h // 16 > w // 9 + 2:  # 长窄屏 2px容差 获取ui描绘的高度
        uih = int(w / 9 * 16)
    else:
        uih = h
    # uiw = int(uih / 16 * 9)

    # 如果游戏结束 点击再来一局
    left = int(w / 2)  # 按钮半宽约uiw//5
    # 根据9:16实测按钮高度中心0.825 按钮半高约uiw//28
    top = int((h - uih) / 2 + uih * 0.825)
    if gameover:
        return left, top

    # 游戏中点击 随机位置防 ban
    left = random.randint(w // 4, w - 20)  # 避开左下角按钮
    top = random.randint(h * 3 // 4, h - 20)
    return left, top

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def jump(piece_x, board_x, im, swipe_x1, swipe_y1):
    distanceX = abs(board_x - piece_x)  # 起点到目标的水平距离
    shortEdge = min(im.size)  # 屏幕宽度
    jumpPercent = distanceX / shortEdge  # 跳跃百分比
    jumpFullWidth = 1700  # 跳过整个宽度 需要按压的毫秒数
    press_time = round(jumpFullWidth * jumpPercent)  # 按压时长
    press_time = 0 if not press_time else max(
        press_time, 200)  # press_time大于0时限定最小值
    print('%-12s %.2f%% (%s/%s) | Press: %sms' %
          ('Distance:', jumpPercent * 100, distanceX, shortEdge, press_time))

    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=swipe_x1,
        y1=swipe_y1,
        x2=swipe_x1 + random.randint(-10, 10),  # 模拟位移
        y2=swipe_y1 + random.randint(-10, 10),
        duration=press_time
    )
    os.system(cmd)

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def main():
    check_screenshot()  # 检查截图

    count = 0
    while True:
        count += 1
        print('---\n%-12s %s (%s)' % ('Times:', count, int(time.time())))

        # 获取截图
        binary_screenshot = pull_screenshot()
        im = Image.open(BytesIO(binary_screenshot))
        w, h = im.size
        if w > h:
            im = im.rotate(-90, expand=True)  # 添加图片方向判断
        # print('image | w:%s | h:%s'%(w,h))

        # 获取棋子和 board 的位置
        piece_x, board_x = find_piece_and_board(im)
        gameover = 0 if all((piece_x, board_x)) else 1
        swipe_x1, swipe_y1 = set_button_position(
            im, gameover=gameover)  # 随机点击位置

        # 标注截图并显示
        # draw = ImageDraw.Draw(im)
        # draw.line([piece_x, 0, piece_x, h], fill='blue', width=1)  # start
        # draw.line([board_x, 0, board_x, h], fill='red', width=1)  # end
        # draw.ellipse([swipe_x1 - 16, swipe_y1 - 16,
        #               swipe_x1 + 16, swipe_y1 + 16], fill='red')  # click
        # im.show()

        jump(piece_x, board_x, im, swipe_x1, swipe_y1)

        wait = (random.random())**5 * 9 + 1  # 停1~9秒 指数越高平均间隔越短
        print('---\nWait %.3f s...' % wait)
        time.sleep(wait)
        print('Continue!')

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        os.system('adb kill-server')
        print('bye')
        exit(0)
