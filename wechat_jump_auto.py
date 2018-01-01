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
    if not size_str:
        print('请安装ADB及驱动并配置环境变量')
        sys.exit()
    m = re.search('(\d+)x(\d+)', size_str)
    if m:
        width = m.group(1)
        height = m.group(2)
        return "{height}x{width}".format(height=height, width=width)


config = open_accordant_config()

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
    #设置模拟按压各项参数，经过多台手机测试，其中2160x1080建议调整参数为320，1210，720，910
    #使用vivox20，夏普全面屏和小米mix2测试过，均可达到2000+分数（记得在开发者设置打开usb安全验证）
    swipe['x1'], swipe['y1'], swipe['x2'], swipe['y2'] = 320, 410, 320, 410


screenshot_way = 2
screenshot_backup_dir = 'screenshot_backups/'
if not os.path.isdir(screenshot_backup_dir):
    os.mkdir(screenshot_backup_dir)


def pull_screenshot():
    global screenshot_way
    # 新的方法请根据效率及适用性由高到低排序
    if screenshot_way == 2 or screenshot_way == 1:
        process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
        screenshot = process.stdout.read()
        if screenshot_way == 2:
          binary_screenshot = screenshot.replace(b'\r\n', b'\n')
        else:
          binary_screenshot = screenshot.replace(b'\r\r\n', b'\n')
        f = open('autojump.png', 'wb')
        f.write(binary_screenshot)
        f.close()
    elif screenshot_way == 0:
        os.system('adb shell screencap -p /sdcard/autojump.png')
        os.system('adb pull /sdcard/autojump.png .')


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
    top = int(1584 * (h / 1920.0))
    swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top


def jump(distance):
    press_time = distance * press_coefficient
    press_time = max(press_time, 200)   # 设置 200 ms 是最小的按压时间
    press_time = int(press_time)
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=swipe_x1,
        y1=swipe_y1,
        x2=swipe_x2,
        y2=swipe_y2,
        duration=press_time
    )
    print(cmd)
    os.system(cmd)
    return press_time

def find_piece_and_board(im):
    w, h = im.size

    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0
    board_x = 0
    board_y = 0
    scan_x_border = int(w / 8)  # 扫描棋子时的左右边界
    scan_start_y = 0  # 扫描的起始y坐标
    im_pixel=im.load()
    # 以50px步长，尝试探测scan_start_y
    for i in range(int(h / 3), int( h*2 /3 ), 50):
        last_pixel = im_pixel[0,i]
        for j in range(1, w):
            pixel=im_pixel[j,i]
            # 不是纯色的线，则记录scan_start_y的值，准备跳出循环
            if pixel[0] != last_pixel[0] or pixel[1] != last_pixel[1] or pixel[2] != last_pixel[2]:
                scan_start_y = i - 50
                break
        if scan_start_y:
            break
    print('scan_start_y: ', scan_start_y)

    # 从scan_start_y开始往下扫描，棋子应位于屏幕上半部分，这里暂定不超过2/3
    for i in range(scan_start_y, int(h * 2 / 3)):
        for j in range(scan_x_border, w - scan_x_border):  # 横坐标方面也减少了一部分扫描开销
            pixel = im_pixel[j,i]
            # 根据棋子的最低行的颜色判断，找最后一行那些点的平均值，这个颜色这样应该 OK，暂时不提出来
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                piece_x_sum += j
                piece_x_c += 1
                piece_y_max = max(i, piece_y_max)

    if not all((piece_x_sum, piece_x_c)):
        return 0, 0, 0, 0
    piece_x = int(piece_x_sum / piece_x_c);
    piece_y = piece_y_max - piece_base_height_1_2  # 上移棋子底盘高度的一半

    #限制棋盘扫描的横坐标，避免音符bug
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
    last_pixel=im_pixel[board_x,i]

    #从上顶点往下+274的位置开始向上找颜色与上顶点一样的点，为下顶点
    #该方法对所有纯色平面和部分非纯色平面有效，对高尔夫草坪面、木纹桌面、药瓶和非菱形的碟机（好像是）会判断错误
    for k in range(i+274, i, -1): #274取开局时最大的方块的上下顶点距离
        pixel = im_pixel[board_x,k]
        if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) < 10:
            break
    board_y = int((i+k) / 2)

    #如果上一跳命中中间，则下个目标中心会出现r245 g245 b245的点，利用这个属性弥补上一段代码可能存在的判断错误
    #若上一跳由于某种原因没有跳到正中间，而下一跳恰好有无法正确识别花纹，则有可能游戏失败，由于花纹面积通常比较大，失败概率较低
    for l in range(i, i+200):
        pixel = im_pixel[board_x,l]
        if abs(pixel[0] - 245) + abs(pixel[1] - 245) + abs(pixel[2] - 245) == 0:
            board_y = l+10
            break



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


def check_screenshot():
    global screenshot_way
    if os.path.isfile('autojump.png'):
        os.remove('autojump.png')
    if (screenshot_way < 0):
        print('暂不支持当前设备')
        sys.exit()
    pull_screenshot()
    try:
        Image.open('./autojump.png').load()
        print('采用方式{}获取截图'.format(screenshot_way))
    except:
        screenshot_way -= 1
        check_screenshot()

def main():

    dump_device_info()
    check_screenshot()

    while True:
        pull_screenshot()
        im = Image.open('./autojump.png')
        # 获取棋子和 board 的位置
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
        ts = int(time.time())
        print(ts, piece_x, piece_y, board_x, board_y)
        set_button_position(im)
        jump(math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2))
        save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y)
        backup_screenshot(ts)
        time.sleep(1)   # 为了保证截图的时候应落稳了，多延迟一会儿


if __name__ == '__main__':
    main()
