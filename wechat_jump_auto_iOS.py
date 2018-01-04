# -*- coding: utf-8 -*-

"""
# === 思路 ===
# 核心：每次落稳之后截图，根据截图算出棋子的坐标和下一个块顶面的中点坐标，
#      根据两个点的距离乘以一个时间系数获得长按的时间
# 识别棋子：靠棋子的颜色来识别位置，通过截图发现最下面一行大概是一条
           直线，就从上往下一行一行遍历，比较颜色（颜色用了一个区间来比较）
           找到最下面的那一行的所有点，然后求个中点，求好之后再让 Y 轴坐标
           减小棋子底盘的一半高度从而得到中心点的坐标
# 识别棋盘：靠底色和方块的色差来做，从分数之下的位置开始，一行一行扫描，
           由于圆形的块最顶上是一条线，方形的上面大概是一个点，所以就
           用类似识别棋子的做法多识别了几个点求中点，这时候得到了块中点的 X
           轴坐标，这时候假设现在棋子在当前块的中心，根据一个通过截图获取的
           固定的角度来推出中点的 Y 坐标
# 最后：根据两点的坐标算距离乘以系数来获取长按时间（似乎可以直接用 X 轴距离）
"""
import os
import shutil
import time
import math
import random
import json
from PIL import Image, ImageDraw
import wda


with open('config.json', 'r') as f:
    config = json.load(f)


# Magic Number，不设置可能无法正常执行，请根据具体截图从上到下按需设置
under_game_score_y = config['under_game_score_y']
# 长按的时间系数，请自己根据实际情况调节
press_coefficient = config['press_coefficient']
# 二分之一的棋子底座高度，可能要调节
piece_base_height_1_2 = config['piece_base_height_1_2']
# 棋子的宽度，比截图中量到的稍微大一点比较安全，可能要调节
piece_body_width = config['piece_body_width']
time_coefficient = config['press_coefficient']

# 模拟按压的起始点坐标，需要自动重复游戏请设置成“再来一局”的坐标
swipe = config.get('swipe', {
    "x1": 320,
    "y1": 410,
    "x2": 320,
    "y2": 410
    })

c = wda.Client()
s = c.session()

screenshot_backup_dir = 'screenshot_backups/'
if not os.path.isdir(screenshot_backup_dir):
    os.mkdir(screenshot_backup_dir)


def pull_screenshot():
    c.screenshot('1.png')


def jump(distance):
    press_time = distance * time_coefficient / 1000
    print('press time: {}'.format(press_time))
    s.tap_hold(200, 200, press_time)


def backup_screenshot(ts):
    """
    为了方便失败的时候 debug
    """
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)
    shutil.copy('1.png', '{}{}.png'.format(screenshot_backup_dir, ts))


def save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y):
    draw = ImageDraw.Draw(im)
    # 对debug图片加上详细的注释
    draw.line((piece_x, piece_y) + (board_x, board_y), fill=2, width=3)
    draw.line((piece_x, 0, piece_x, im.size[1]), fill=(255, 0, 0))
    draw.line((0, piece_y, im.size[0], piece_y), fill=(255, 0, 0))
    draw.line((board_x, 0, board_x, im.size[1]), fill=(0, 0, 255))
    draw.line((0, board_y, im.size[0], board_y), fill=(0, 0, 255))
    draw.ellipse(
        (piece_x - 10, piece_y - 10, piece_x + 10, piece_y + 10),
        fill=(255, 0, 0))
    draw.ellipse(
        (board_x - 10, board_y - 10, board_x + 10, board_y + 10),
        fill=(0, 0, 255))
    del draw
    im.save('{}{}_d.png'.format(screenshot_backup_dir, ts))


def set_button_position(im):
    """
    将swipe设置为 `再来一局` 按钮的位置
    """
    global swipe_x1, swipe_y1, swipe_x2, swipe_y2
    w, h = im.size
    left = w / 2
    top = 1003 * (h / 1280.0) + 10
    swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top

def find_piece_and_board(im):
    """
    寻找关键坐标
    """
    w, h = im.size

    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0
    board_x = 0
    board_y = 0
    scan_x_border = int(w / 8)  # 扫描棋子时的左右边界
    scan_start_y = 0  # 扫描的起始 y 坐标
    im_pixel = im.load()
    # 以 50px 步长，尝试探测 scan_start_y
    for i in range(int(h / 3), int(h*2 / 3), 50):
        last_pixel = im_pixel[0, i]
        for j in range(1, w):
            pixel = im_pixel[j, i]
            # 不是纯色的线，则记录 scan_start_y 的值，准备跳出循环
            if pixel != last_pixel:
                scan_start_y = i - 50
                break
        if scan_start_y:
            break
    # print('scan_start_y: {}'.format(scan_start_y))

    # 使用像素聚集边界来判断中心
    # j 横坐标
    # i 纵坐标

    pixel_dict_x = dict()
    pixel_dict_y = dict()
    # pixel_dict_y = dict()
    for i in range(scan_start_y, int(h * 2 / 3)):
        # 横坐标方面也减少了一部分扫描开销
        for j in range(scan_x_border, w - scan_x_border):
            pixel = im_pixel[j, i]
            # 根据棋子颜色，进行像素积累记录，棋子最宽的地方即是纵坐标位置，同理可得
            # if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
            if (50 < pixel[0] < 60) and (50 < pixel[1] < 60) and (85 < pixel[2] < 105):
                if j not in pixel_dict_x:
                    pixel_dict_x[j] = 0
                pixel_dict_x[j] +=1
                if i not in pixel_dict_y:
                    pixel_dict_y[i] = 0
                pixel_dict_y[i] +=1

    piece_x = sorted(pixel_dict_x,key=lambda x:pixel_dict_x[x])[-1]  
    piece_y = sorted(pixel_dict_y,key=lambda x:pixel_dict_y[x])[-1]
    # print (piece_x, piece_y)


    # 限制棋盘扫描的横坐标，避免音符 bug
    if piece_x < w/2:
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

            # 获取棋子半径
            if abs(j - piece_x) < pixel_dict_y[sorted(pixel_dict_y,key=lambda x:pixel_dict_y[x])[-1]]:
                  continue

            # 修掉圆顶的时候一条线导致的小 bug，这个颜色判断应该 OK，暂时不提出来
            if abs(pixel[0] - last_pixel[0]) \
                    + abs(pixel[1] - last_pixel[1]) \
                    + abs(pixel[2] - last_pixel[2]) > 10:
                board_x_sum += j
                board_x_c += 1
        if board_x_sum:
            board_x = board_x_sum / board_x_c
    last_pixel = im_pixel[board_x, i]

    # 从上顶点往下 +274 的位置开始向上找颜色与上顶点一样的点，为下顶点
    # 该方法对所有纯色平面和部分非纯色平面有效，对高尔夫草坪面、木纹桌面、
    # 药瓶和非菱形的碟机（好像是）会判断错误
    for k in range(i+274, i, -1):  # 274 取开局时最大的方块的上下顶点距离
        pixel = im_pixel[board_x, k]
        if abs(pixel[0] - last_pixel[0]) \
                + abs(pixel[1] - last_pixel[1]) \
                + abs(pixel[2] - last_pixel[2]) < 10:
            break
    board_y = int((i+k) / 2)


    # 增加对高尔夫草坪面、木纹桌面、药瓶和非菱形的碟机判断，如果非中心，特别是边角情况，则上下两边界限将会不同，进行修正工作
    if im_pixel[board_x, board_y+3] != im_pixel[board_x, board_y-3]:
        board_y = int((i*2+274/2) / 2)
        #print ('here board_y',board_y)

    # 如果上一跳命中中间，则下个目标中心会出现 r245 g245 b245 的点，利用这个
    # 属性弥补上一段代码可能存在的判断错误
    # 若上一跳由于某种原因没有跳到正中间，而下一跳恰好有无法正确识别花纹，则有
    # 可能游戏失败，由于花纹面积通常比较大，失败概率较低
    for j in range(i, i+200):
        pixel = im_pixel[board_x, j]
        if abs(pixel[0] - 245) + abs(pixel[1] - 245) + abs(pixel[2] - 245) == 0:
            board_y = j + 10
            break

    if not all((board_x, board_y)):
        return 0, 0, 0, 0
    return piece_x, piece_y, board_x, board_y



def main():
    while True:
        pull_screenshot()
        im = Image.open("./1.png")

        # 获取棋子和 board 的位置
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
        ts = int(time.time())
        print(ts, piece_x, piece_y, board_x, board_y)
        if piece_x == 0:
            return

        set_button_position(im)
        distance = math.sqrt(
            (board_x - piece_x) ** 2 + (board_y - piece_y) ** 2)
        jump(distance)

        save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y)
        backup_screenshot(ts)
        # 为了保证截图的时候应落稳了，多延迟一会儿，随机值防 ban
        time.sleep(random.uniform(1, 1.1))


if __name__ == '__main__':
    main()
