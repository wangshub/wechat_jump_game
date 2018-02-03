# -*- coding: utf-8 -*-

"""
=== 思路 ===
核心：每次落稳之后截图，根据截图算出棋子的坐标和下一个块顶面的中点坐标，
    根据两个点的距离乘以一个时间系数获得长按的时间
识别棋子：靠棋子的颜色来识别位置，通过截图发现最下面一行大概是一条
    直线，就从上往下一行一行遍历，比较颜色（颜色用了一个区间来比较）
    找到最下面的那一行的所有点，然后求个中点，求好之后再让 Y 轴坐标
    减小棋子底盘的一半高度从而得到中心点的坐标
识别棋盘：靠底色和方块的色差来做，从分数之下的位置开始，一行一行扫描，
    由于圆形的块最顶上是一条线，方形的上面大概是一个点，所以就
    用类似识别棋子的做法多识别了几个点求中点，这时候得到了块中点的 X
    轴坐标，这时候假设现在棋子在当前块的中心，根据一个通过截图获取的
    固定的角度来推出中点的 Y 坐标
最后：根据两点的坐标算距离乘以系数来获取长按时间（似乎可以直接用 X 轴距离）
"""
from __future__ import print_function, division

import math
import os
import random
import sys
import time
from PIL import Image
from six.moves import input

try:
    from common import adb, debug, config, screenshot, UnicodeStreamFilter
except Exception as ex:
    print(ex)
    print('请将脚本放在项目根目录中运行')
    print('请检查项目根目录中的 common 文件夹是否存在')
    exit(-1)

VERSION = "1.2.1"

# DEBUG 开关，需要调试的时候请改为 True，不需要调试的时候为 False
DEBUG_SWITCH = False

# Magic Number，不设置可能无法正常执行，请根据具体截图从上到下按需
# 设置，设置保存在 config 文件夹中
config = config.open_accordant_config()
under_game_score_y = config['under_game_score_y']
# 长按的时间系数，请自己根据实际情况调节
press_coefficient = config['press_coefficient']
# 二分之一的棋子底座高度，可能要调节
piece_base_height_1_2 = config['piece_base_height_1_2']
# 棋子的宽度，比截图中量到的稍微大一点比较安全，可能要调节
piece_body_width = config['piece_body_width']
# 图形中圆球的直径，可以利用系统自带画图工具，用直线测量像素，如果可以实现自动识别圆球直径，那么此处将可实现全自动。
# head_diameter = config.get('head_diameter', 60)

#用于平均测得的head_diameter
head_diameter_lst = []


def set_button_position(im):
    """
    将 swipe 设置为 `再来一局` 按钮的位置
    """
    global swipe_x1, swipe_y1, swipe_x2, swipe_y2
    w, h = im.size
    left = int(w / 2)
    top = int(1584 * (h / 1920.0))
    left = int(random.uniform(left - 50, left + 50))
    top = int(random.uniform(top - 10, top + 10))  # 随机防 ban
    swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top


def jump(distance, delta_piece_y):
    """
    跳跃一定的距离
    """
    # 计算程序长度与截图测得的距离的比例
    scale = 0.945 * 2 / head_diameter
    actual_distance = distance * scale * (math.sqrt(6) / 2)
    press_time = (-945 + math.sqrt(945 ** 2 + 4 * 105 * 36 * actual_distance)) / (2 * 105) * 1000
    press_time = max(press_time, 200)  # 设置 200ms 是最小的按压时间
    press_time = int(press_time)

    cmd = 'shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=swipe_x1,
        y1=swipe_y1,
        x2=swipe_x2,
        y2=swipe_y2,
        duration=press_time + delta_piece_y
    )
    print('{} {}'.format(adb.adb_path, cmd))
    adb.run(cmd)
    return press_time


def find_piece_and_board(im):
    """
    寻找关键坐标
    """
    w, h = im.size
    points = []                 # 所有满足色素的点集合
    piece_y_max = 0
    board_x = 0
    board_y = 0
    scan_x_border = int(w / 8)  # 扫描棋子时的左右边界
    scan_start_y = 0  # 扫描的起始 y 坐标
    im_pixel = im.load()
    # 以 50px 步长，尝试探测 scan_start_y
    for i in range(int(h / 3), int(h * 2 / 3), 50):
        last_pixel = im_pixel[0, i]
        for j in range(1, w):
            pixel = im_pixel[j, i]
            # 不是纯色的线，则记录 scan_start_y 的值，准备跳出循环
            if pixel != last_pixel:
                scan_start_y = i - 50
                break
        if scan_start_y:
            break
    print('scan_start_y: {}'.format(scan_start_y))

    # 从 scan_start_y 开始往下扫描，棋子应位于屏幕上半部分，这里暂定不超过 2/3
    for i in range(scan_start_y, int(h * 2 / 3)):
        # 横坐标方面也减少了一部分扫描开销
        for j in range(scan_x_border, w - scan_x_border):
            pixel = im_pixel[j, i]
            # 根据棋子的最低行的颜色判断，找最后一行那些点的平均值，这个颜
            # 色这样应该 OK，暂时不提出来
            if (50 < pixel[0] < 60) \
                    and (53 < pixel[1] < 63) \
                    and (95 < pixel[2] < 110):
                points.append((j, i))
                piece_y_max = max(i, piece_y_max)

    bottom_x = [x for x,y in points if y == piece_y_max]  # 所有最底层的点的横坐标
    if not bottom_x:

        return 0, 0, 0, 0, 0

    piece_x = int(sum(bottom_x) / len(bottom_x))  # 中间值
    piece_y = piece_y_max - piece_base_height_1_2  # 上移棋子底盘高度的一半

    # 限制棋盘扫描的横坐标，避免音符 bug
    if piece_x < w / 2:
        board_x_start = piece_x
        board_x_end = w
    else:
        board_x_start = 0
        board_x_end = piece_x

    for i in range(int(h / 3), int(h * 2 / 3)):
        last_pixel = im_pixel[0, i]
        if board_x or board_y:
            break
        board_x_sum = 0
        board_x_c = 0

        for j in range(int(board_x_start), int(board_x_end)):
            pixel = im_pixel[j, i]
            # 修掉脑袋比下一个小格子还高的情况的 bug
            if abs(j - piece_x) < piece_body_width:
                continue

            # 检查Y轴下面5个像素， 和背景色相同， 那么是干扰
            ver_pixel = im_pixel[j, i + 5]
            if abs(pixel[0] - last_pixel[0]) \
                    + abs(pixel[1] - last_pixel[1]) \
                    + abs(pixel[2] - last_pixel[2]) > 10 \
                    and abs(ver_pixel[0] - last_pixel[0]) \
                    + abs(ver_pixel[1] - last_pixel[1]) \
                    + abs(ver_pixel[2] - last_pixel[2]) > 10:
                board_x_sum += j
                board_x_c += 1
        if board_x_sum:
            board_x = board_x_sum / board_x_c
    last_pixel = im_pixel[board_x, i]


    #首先找到游戏的对称中心，由对称中心做辅助线与x=board_x直线的交点即为棋盘的中心位置
    #有了对称中心，可以知道棋子在棋盘上面的相对位置（偏高或偏低，偏高的话测量值比实际值大，
    #偏低相反。最后通过delta_piece_y来对跳跃时间进行微调
    center_x = w/ 2 + 24
    center_y = h/ 2 + 17
    if piece_x > center_x:
        board_y = round((25.5/ 43.5) * (board_x - center_x) + center_y)
        delta_piece_y = piece_y - round((25.5/ 43.5) * (piece_x - center_x) + center_y)
    else:
        board_y = round(-(25.5/ 43.5) * (board_x - center_x) + center_y)
        delta_piece_y = piece_y - round(-(25.5/ 43.5) * (piece_x - center_x) + center_y)

    if not all((board_x, board_y)):
        return 0, 0, 0, 0, 0
    return piece_x, piece_y, board_x, board_y, delta_piece_y


def find_head_diameter(im):
    #找出棋子头部直径，用于调整按压时间
    top = None
    bottom = None
    last = None
    w, h = im.size
    scan_x_border = int(w / 8)
    im_pixel = im.load()
    meet_head = False
    for j in range(int(h / 3), int(h * 2 / 3)):
        is_head = False
        for i in range(scan_x_border, w - scan_x_border):
                pixel = im_pixel[i, j]
                if (50 < pixel[0] < 65) \
                        and (50 < pixel[1] < 70) \
                        and (60 < pixel[2] < 90):
                    if not meet_head:
                        top = (i, j)
                        meet_head = True
                        is_head = True
                        break
                    else:
                        last = (i, j)
                        is_head = True
                        break

        if meet_head and not is_head:
            bottom = (i, j)
            if abs(last[0] - top[0]) > 10: #检查横坐标是否相差太大
                return 0
            else:
                head_diameter_finded = bottom[1] - top[1]
                break
    if not meet_head or not bottom:
        return 0
    else:
        return(head_diameter_finded)

def check_head_diameter(im):
    #设置和检查head_diameter
    global head_diameter
    global head_diameter_lst
    head_diameter_temp = 60;

    if len(head_diameter_lst) > 3: #如果已经有三个了，就直接pass
        pass
    else:
        head_diameter_init = find_head_diameter(im)

        if abs(head_diameter_init - 60) > 30: #防止有bug
            head_diameter = head_diameter_temp
        else:
            head_diameter_lst.append(head_diameter_init)

            #取平均数
            head_diameter = round(sum(head_diameter_lst)/ len(head_diameter_lst))
        print("head_diameter : ", head_diameter)


def yes_or_no(prompt, true_value='y', false_value='n', default=True):
    """
    检查是否已经为启动程序做好了准备
    """
    default_value = true_value if default else false_value
    prompt = '{} {}/{} [{}]: '.format(prompt, true_value,
                                      false_value, default_value)
    i = input(prompt)
    if not i:
        return default
    while True:
        if i == true_value:
            return True
        elif i == false_value:
            return False
        prompt = 'Please input {} or {}: '.format(true_value, false_value)
        i = input(prompt)


def main():
    """
    主函数
    """
    op = yes_or_no('请确保手机打开了 ADB 并连接了电脑，'
                   '然后打开跳一跳并【开始游戏】后再用本程序，确定开始？')
    if not op:
        print('bye')
        return
    print('程序版本号：{}'.format(VERSION))
    print('激活窗口并按 CONTROL + C 组合键退出')
    debug.dump_device_info()
    screenshot.check_screenshot()

    i, next_rest, next_rest_time = (0, random.randrange(3, 10),
                                    random.randrange(5, 10))
    while True:
        screenshot.pull_screenshot()
        im = Image.open('./autojump.png')

        #检查和获取 head_diameter
        check_head_diameter(im)

        # 获取棋子和 board 的位置
        piece_x, piece_y, board_x, board_y , delta_piece_y = find_piece_and_board(im)
        ts = int(time.time())
        print(ts, piece_x, piece_y, board_x, board_y)
        set_button_position(im)
        jump(math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2), delta_piece_y)
        if DEBUG_SWITCH:
            debug.save_debug_screenshot(ts, im, piece_x,
                                        piece_y, board_x, board_y)
            debug.backup_screenshot(ts)
        im.close()
        i += 1
        if i == next_rest:
            print('已经连续打了 {} 下，休息 {}s'.format(i, next_rest_time))
            for j in range(next_rest_time):
                sys.stdout.write('\r程序将在 {}s 后继续'.format(next_rest_time - j))
                sys.stdout.flush()
                time.sleep(1)
            print('\n继续')
            i, next_rest, next_rest_time = (0, random.randrange(30, 100),
                                            random.randrange(10, 60))
        # 为了保证截图的时候应落稳了，多延迟一会儿，随机值防 ban
        time.sleep(random.uniform(1.2, 1.4))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        adb.run('kill-server')
        print('bye')
        exit(0)
