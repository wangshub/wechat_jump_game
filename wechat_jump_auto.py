# coding: utf-8
import os
import sys
import subprocess
import shutil
import time
import math
from PIL import Image, ImageDraw
import random
import json
import re
import cv2
import numpy as np
import datetime


# === 思路 ===
# 核心：每次落稳之后截图，根据截图算出棋子的坐标和下一个块顶面的中点坐标，
#      根据两个点的距离乘以一个时间系数获得长按的时间
# 识别棋子：靠棋子的颜色来识别位置，通过截图发现最下面一行大概是一条直线，就从上往下一行一行遍历，
#      比较颜色（颜色用了一个区间来比较）找到最下面的那一行的所有点，然后求个中点，
#      求好之后再让 Y 轴坐标减小棋子底盘的一半高度从而得到中心点的坐标
# 识别棋盘：靠底色和方块的色差来做，从分数之下的位置开始，一行一行扫描，由于圆形的块最顶上是一条线，
#      方形的上面大概是一个点，所以就用类似识别棋子的做法多识别了几个点求中点，
#      这时候得到了块中点的 X 轴坐标，这时候假设现在棋子在当前块的中心，
#      根据一个通过截图获取的固定的角度来推出中点的 Y 坐标
# 最后：根据两点的坐标算距离乘以系数来获取长按时间（似乎可以直接用 X 轴距离）


# TODO: 解决定位偏移的问题
# TODO: 看看两个块中心到中轴距离是否相同，如果是的话靠这个来判断一下当前超前还是落后，便于矫正
# TODO: 一些固定值根据截图的具体大小计算
# TODO: 直接用 X 轴距离简化逻辑

def open_accordant_config():
    screen_size = _get_screen_size()
    config_file = "{path}/config/{screen_size}/config.json".format(
        path=sys.path[0],
        screen_size=screen_size
    )
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            print("Load config file from {}".format(config_file))
            return json.load(f)
    else:
        with open('{}/config/default.json'.format(sys.path[0]), 'r') as f:
            print("Load default config")
            return json.load(f)


def _get_screen_size():
    size_str = os.popen('adb shell wm size').read()
    m = re.search('(\d+)x(\d+)', size_str)
    if m:
        width = m.group(1)
        height = m.group(2)
        return "{height}x{width}".format(height=height, width=width)


config = open_accordant_config()
# 获取得分需要的信息
number_list = [(cv2.imread("./train_data/number/%d.png" % i, 0)) for i in range(0, 10)]

# Magic Number，不设置可能无法正常执行，请根据具体截图从上到下按需设置
under_game_score_y = config['under_game_score_y']
press_coefficient = config['press_coefficient']       # 长按的时间系数，请自己根据实际情况调节
piece_base_height_1_2 = config['piece_base_height_1_2']   # 二分之一的棋子底座高度，可能要调节
piece_body_width = config['piece_body_width']             # 棋子的宽度，比截图中量到的稍微大一点比较安全，可能要调节

# 模拟按压的起始点坐标，需要自动重复游戏请设置成“再来一局”的坐标
if config.get('swipe'):
    swipe = config['swipe']
else:
    swipe = {}
    swipe['x1'], swipe['y1'], swipe['x2'], swipe['y2'] = 320, 410, 320, 410


screenshot_backup_dir = 'screenshot_backups/'
if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)

def del_screenshot(ts):
    if os.path.isfile('{}{}_d.png'.format(screenshot_backup_dir, ts)):
        os.remove('{}{}_d.png'.format(screenshot_backup_dir, ts))
        os.remove('{}{}_d1.png'.format(screenshot_backup_dir, ts))
        os.remove('{}{}.png'.format(screenshot_backup_dir, ts))


def pull_screenshot():
    # 使用线上的代码获取截图会出错
    # process = subprocess.Popen('adb shell screencap', shell=True, stdout=subprocess.PIPE)
    # screenshot = process.stdout.read()
    # if sys.platform == 'win32':
    #     screenshot = screenshot.replace(b'\r\n', b'\n')
    # f = open('autojump.png', 'wb')
    # f.write(screenshot)
    # f.close()
    os.system("adb shell screencap -p /sdcard/autojump.png")
    os.system("adb pull /sdcard/autojump.png .")

def backup_screenshot(ts):
    # 为了方便失败的时候 debug
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)
    shutil.copy('autojump.png', '{}{}.png'.format(screenshot_backup_dir, ts))


def save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y):
    draw = ImageDraw.Draw(im)
    # 对debug图片加上详细的注释
    draw.line((piece_x, piece_y) + (board_x, board_y), fill=2, width=3)
    draw.line((piece_x, 0, piece_x, im.size[1]), fill=(255, 0, 0))
    draw.line((0, piece_y, im.size[0], piece_y), fill=(255, 0, 0))
    draw.line((board_x, 0, board_x, im.size[1]), fill=(0, 0, 255))
    draw.line((0, board_y, im.size[0], board_y), fill=(0, 0, 255))
    draw.ellipse((piece_x - 10, piece_y - 10, piece_x + 10, piece_y + 10), fill=(255, 0, 0))
    draw.ellipse((board_x - 10, board_y - 10, board_x + 10, board_y + 10), fill=(0, 0, 255))
    del draw
    im.save('{}{}_d.png'.format(screenshot_backup_dir, ts))


def set_button_position(im):
    # 将swipe设置为 `再来一局` 按钮的位置
    global swipe_x1, swipe_y1, swipe_x2, swipe_y2
    w, h = im.size
    left = w / 2
    top = 1003 * (h / 1280.0) + 10
    swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top


def jump(distance):
    press_time = distance * press_coefficient
    press_time = max(press_time, 200)   # 设置 200 ms 是最小的按压时间
    press_time = int(press_time)
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=swipe['x1'],
        y1=swipe['y1'],
        x2=swipe['x2'],
        y2=swipe['y2'],
        duration=press_time
    )
    print(cmd)
    os.system(cmd)

def get_number(image):
    # 获取每一位的数字
    global number_list
    for item in range(0, 10):
        res = cv2.matchTemplate(image, number_list[item], cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.9)
        if len(loc[0]) > 0:
            return item
    return 0

def get_score(image):
    # 获取当前得分
    img = cv2.imread(image)
    global config
    score_min_y = config['score_min_y']
    score_max_y = config['score_max_y']
    score_x1_min = config['score_x1_min']
    score_x1_max = config['score_x1_max']
    score_x_diff = config['score_x_diff']
    number_real = [get_number(cv2.cvtColor(img[score_min_y:score_max_y,score_x1_min + score_x_diff * x:score_x1_max + score_x_diff * x], cv2.COLOR_RGB2GRAY)) for x in range(0, 5)]
    last = 0
    for i in range(0, 5):
        if number_real[i] != 0:
            last = i
            break
    number = 0
    for i in range(4, last - 1, -1):
        number = number * 10 + number_real[i]
    return number

def find_piece(image, target, ts):
    # 获取特殊的位置，即小人的位置和可能的目标点的位置
    img_rgb = cv2.imread(image)
    hight = img_rgb.shape[0]
    min_hight = int(hight/3)
    img_rgb2 = img_rgb[min_hight:hight-1]
    img_gray = cv2.cvtColor(img_rgb2, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(target, 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 1.0
    threshold_step = 0.1
    ite_time = 0
    flag = False
    last_flag = False
    while True:
        loc = np.where(res >= threshold)
        ite_time += 1
        if len(loc[0]) == 0:
            last_flag = False
            if flag != last_flag:
                threshold_step *= 0.5
                flag = last_flag
            threshold -= threshold_step
        elif len(loc[0]) > 1:
            last_flag = True
            if flag != last_flag:
                threshold_step *= 0.5
                flag = last_flag
            threshold += threshold_step
        else:
            break
        if threshold < 0.7 or ite_time > 3000 or threshold_step < 0.0000000001:
            return 0, 0
    # 画出debug信息的图片
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_rgb, (pt[0], pt[1] + min_hight), (pt[0] + w, pt[1] + h + min_hight), (7,249,151), 1)   
        cv2.circle(img_rgb, (int(pt[0] + w/2), int(pt[1] + h - 25 + min_hight)), 2, (7,249,151), 1)
    if ts != 0:
        cv2.imwrite('{}{}_d1.png'.format(screenshot_backup_dir, ts), img_rgb)
    cv2.destroyAllWindows()

    return loc[1][0]+w/2 + 0.8, (loc[0][0] + h - 25 + min_hight)


def find_piece_and_board(im, image2, ts):
    w, h = im.size

    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0
    board_x = 0
    board_y = 0
    scan_x_border = int(w / 8)  # 扫描棋子时的左右边界
    scan_start_y = 0  # 扫描的起始y坐标
    im_pixel=im.load()

    piece_x, piece_y = find_piece(image2, "train_data/character3.png", ts)
    if not os.path.isfile('{}{}_d1.png'.format(screenshot_backup_dir, ts)):
        print("Error and Exit")
        sys.exit(-1)
    board_x, board_y = find_piece('{}{}_d1.png'.format(screenshot_backup_dir, ts), "train_data/character4.png", ts)
    if board_x != 0 and board_y < piece_y and abs(board_x - piece_x) > 100:
        print("\033[91m" + "method2" + "\033[0m")
        return piece_x, piece_y, board_x, board_y

    print("\033[93m" + "method1" + "\033[0m")
    # 如果没有找到小圆点或者找到的小圆点位置明显有问题，就使用原来的方式

    for i in range(int(h / 3), int(h * 2 / 3)):
        last_pixel = im_pixel[0, i]
        if board_x or board_y:
            break
        board_x_sum = 0
        board_x_c = 0

        for j in range(w):
            pixel = im_pixel[j,i]
            # 修掉脑袋比下一个小格子还高的情况的 bug
            if abs(j - piece_x) < piece_body_width:
                continue

            # 修掉圆顶的时候一条线导致的小 bug，这个颜色判断应该 OK，暂时不提出来
            if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) > 10:
                board_x_sum += j
                board_x_c += 1
        if board_x_sum:
            board_x = board_x_sum / board_x_c
    # 按实际的角度来算，找到接近下一个 board 中心的坐标 这里的角度应该是30°,值应该是tan 30°, math.sqrt(3) / 3
    board_y = piece_y - abs(board_x - piece_x) * math.sqrt(3) / 3

    if not all((board_x, board_y)):
        return 0, 0, 0, 0

    return piece_x, piece_y, board_x, board_y


def dump_device_info():
    size_str = os.popen('adb shell wm size').read()
    device_str = os.popen('adb shell getprop ro.product.model').read()
    density_str = os.popen('adb shell wm density').read()
    print("如果你的脚本无法工作，上报issue时请copy如下信息:\n**********\
        \nScreen: {size}\nDensity: {dpi}\nDeviceType: {type}\nOS: {os}\nPython: {python}\n**********".format(
            size=size_str.strip(),
            type=device_str.strip(),
            dpi=density_str.strip(),
            os=sys.platform,
            python=sys.version
    ))

def check_adb():
    flag = os.system('adb devices')
    if flag == 1:
        print('请安装ADB并配置环境变量')
        sys.exit()

def main():
    dump_device_info()
    check_adb()
    last_score = 0
    last_ts = 0
    while True:
        pull_screenshot()
        im = Image.open('./autojump.png')
        current_score = get_score("./autojump.png")
        # 只保留特定分数间隔的debug文件，防止文件过多
        if (current_score - last_score) not in [0, 1, 2, 3, 6, 11, 17, 31]:
            del_screenshot(last_ts)
        # 获取棋子和 board 的位置
        ts = int(time.time())
        # 获取棋子和 board 的位置
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im, "./autojump.png", ts)
        set_button_position(im)
        jump(math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2))
        save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y)
        backup_screenshot(ts)
        time.sleep(random.uniform(1, 1.1))   # 为了保证截图的时候应落稳了，多延迟一会儿
        last_score = current_score
        last_ts = ts


if __name__ == '__main__':
    main()
