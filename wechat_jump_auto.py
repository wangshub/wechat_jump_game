# coding: utf-8
import os
import sys
import subprocess
import time
import math
from PIL import Image
import random
from WechatJump import Debug, Config

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

debug_switch = False # debug开关，需要调试的时候请改为：True
config = Config.open_accordant_config()

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

def pull_screenshot():
    process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    screenshot = process.stdout.read()
    if sys.platform == 'win32':
        screenshot = screenshot.replace(b'\r\n', b'\n')
    f = open('autojump.png', 'wb')
    f.write(screenshot)
    f.close()


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

# 转换色彩模式hsv2rgb
def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

# 转换色彩模式rgb2hsv
def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v


def find_piece_and_board(im):
    w, h = im.size

    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0
    board_x = 0
    board_y = 0

    left_value = 0
    left_count = 0
    right_value = 0
    right_count = 0
    from_left_find_board_y = 0
    from_right_find_board_y = 0


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
    piece_x = piece_x_sum / piece_x_c
    piece_y = piece_y_max - piece_base_height_1_2  # 上移棋子底盘高度的一半

    for i in range(int(h / 3), int(h * 2 / 3)):

        last_pixel = im_pixel[0, i]
        # 计算阴影的RGB值,通过photoshop观察,阴影部分其实就是背景色的明度V 乘以0.7的样子
        h, s, v = rgb2hsv(last_pixel[0], last_pixel[1], last_pixel[2])
        r, g, b = hsv2rgb(h, s, v * 0.7)

        if from_left_find_board_y and from_right_find_board_y:
            break

        if not board_x:
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
        else:
            # 继续往下查找,从左到右扫描,找到第一个与背景颜色不同的像素点,记录位置
            # 当有连续3个相同的记录时,表示发现了一条直线
            # 这条直线即为目标board的左边缘
            # 然后当前的 y 值减 3 获得左边缘的第一个像素
            # 就是顶部的左边顶点
            for j in range(w):
                pixel = im_pixel[j, i]
                # 修掉脑袋比下一个小格子还高的情况的 bug
                if abs(j - piece_x) < piece_body_width:
                    continue
                if (abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2])
                        > 10) and (abs(pixel[0] - r) + abs(pixel[1] - g) + abs(pixel[2] - b) > 10):
                    if left_value == j:
                        left_count = left_count+1
                    else:
                        left_value = j
                        left_count = 1

                    if left_count > 3:
                        from_left_find_board_y = i - 3
                    break
            # 逻辑跟上面类似,但是方向从右向左
            # 当有遮挡时,只会有一边有遮挡
            # 算出来两个必然有一个是对的
            for j in range(w)[::-1]:
                pixel = im_pixel[j, i]
                # 修掉脑袋比下一个小格子还高的情况的 bug
                if abs(j - piece_x) < piece_body_width:
                    continue
                if (abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2])
                    > 10) and (abs(pixel[0] - r) + abs(pixel[1] - g) + abs(pixel[2] - b) > 10):
                    if right_value == j:
                        right_count = left_count + 1
                    else:
                        right_value = j
                        right_count = 1

                    if right_count > 3:
                        from_right_find_board_y = i - 3
                    break

    # 如果顶部像素比较多,说明图案近圆形,相应的求出来的值需要增大,这里暂定增大顶部宽的三分之一
    if board_x_c > 5:
        from_left_find_board_y = from_left_find_board_y + board_x_c / 3
        from_right_find_board_y = from_right_find_board_y + board_x_c / 3

    # 按实际的角度来算，找到接近下一个 board 中心的坐标 这里的角度应该是30°,值应该是tan 30°,math.sqrt(3) / 3
    board_y = piece_y - abs(board_x - piece_x) * math.sqrt(3) / 3

    # 从左从右取出两个数据进行对比,选出来更接近原来老算法的那个值
    if abs(board_y - from_left_find_board_y) > abs(from_right_find_board_y):
        new_board_y = from_right_find_board_y
    else:
        new_board_y = from_left_find_board_y

    if not all((board_x, board_y)):
        return 0, 0, 0, 0

    return piece_x, piece_y, board_x, new_board_y


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

    h, s, v = rgb2hsv(201, 204, 214)
    print(h, s, v)
    r, g, b = hsv2rgb(h, s, v*0.7)
    print(r, g, b)

    dump_device_info()
    check_adb()
    while True:
        pull_screenshot()
        im = Image.open('./autojump.png')
        # 获取棋子和 board 的位置
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
        set_button_position(im)
        jump(math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2))
        if debug_switch:
            ts = int(time.time())
            print(ts, piece_x, piece_y, board_x, board_y)
            Debug.save_debug_screenshot(ts, im, piece_x, piece_y, board_x, board_y)
            Debug.backup_screenshot(ts)
        time.sleep(random.uniform(1.2, 1.4))   # 为了保证截图的时候应落稳了，多延迟一会儿


if __name__ == '__main__':
    main()
