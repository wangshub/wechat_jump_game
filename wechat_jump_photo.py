# coding: utf-8

import os
import sys
import subprocess
import time
import math
from PIL import Image
import random
import simplejson as json

def open_accordant_config(screen_size = '1920x1080'):
    print('start open_accordant_config screen_size=%s'%(screen_size))
    '''
    调用配置文件
    '''
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


'''
//已改为直接读取
# Magic Number，不设置可能无法正常执行，请根据具体截图从上到下按需设置，设置保存在 config 文件夹中
under_game_score_y = config['under_game_score_y']
press_coefficient = config['press_coefficient']       # 长按的时间系数，请自己根据实际情况调节
piece_base_height_1_2 = config['piece_base_height_1_2']   # 二分之一的棋子底座高度，可能要调节
piece_body_width = config['piece_body_width']             # 棋子的宽度，比截图中量到的稍微大一点比较安全，可能要调节
'''

def calcPressTime(distance,config):
    press_time = distance * config['press_coefficient']
    press_time = max(press_time, 200)   # 设置 200ms 是最小的按压时间
    press_time = int(press_time)
    return press_time


def find_piece_and_board(im,config):
    '''
    寻找关键坐标
    '''
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
            if pixel[0] != last_pixel[0] or pixel[1] != last_pixel[1] or pixel[2] != last_pixel[2]:
                scan_start_y = i - 50
                break
        if scan_start_y:
            break
    print('scan_start_y: {}'.format(scan_start_y))

    # 从 scan_start_y 开始往下扫描，棋子应位于屏幕上半部分，这里暂定不超过 2/3
    for i in range(scan_start_y, int(h * 2 / 3)):
        for j in range(scan_x_border, w - scan_x_border):  # 横坐标方面也减少了一部分扫描开销
            pixel = im_pixel[j, i]
            # 根据棋子的最低行的颜色判断，找最后一行那些点的平均值，这个颜色这样应该 OK，暂时不提出来
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                piece_x_sum += j
                piece_x_c += 1
                piece_y_max = max(i, piece_y_max)

    if not all((piece_x_sum, piece_x_c)):
        return 0, 0, 0, 0
    piece_x = int(piece_x_sum / piece_x_c)
    piece_y = piece_y_max - config['piece_base_height_1_2']  # 上移棋子底盘高度的一半

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
            # 修掉脑袋比下一个小格子还高的情况的 bug
            if abs(j - piece_x) < config['piece_body_width']:
                continue

            # 修掉圆顶的时候一条线导致的小 bug，这个颜色判断应该 OK，暂时不提出来
            if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) > 10:
                board_x_sum += j
                board_x_c += 1
        if board_x_sum:
            board_x = board_x_sum / board_x_c
    last_pixel = im_pixel[board_x, i]

    # 从上顶点往下 +274 的位置开始向上找颜色与上顶点一样的点，为下顶点
    # 该方法对所有纯色平面和部分非纯色平面有效，对高尔夫草坪面、木纹桌面、药瓶和非菱形的碟机（好像是）会判断错误
    for k in range(i+274, i, -1): # 274 取开局时最大的方块的上下顶点距离
        pixel = im_pixel[board_x, k]
        if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) < 10:
            break
    board_y = int((i+k) / 2)

    # 如果上一跳命中中间，则下个目标中心会出现 r245 g245 b245 的点，利用这个属性弥补上一段代码可能存在的判断错误
    # 若上一跳由于某种原因没有跳到正中间，而下一跳恰好有无法正确识别花纹，则有可能游戏失败，由于花纹面积通常比较大，失败概率较低
    for l in range(i, i+200):
        pixel = im_pixel[board_x, l]
        if abs(pixel[0] - 245) + abs(pixel[1] - 245) + abs(pixel[2] - 245) == 0:
            board_y = l+10
            break

    if not all((board_x, board_y)):
        return 0, 0, 0, 0

    return piece_x, piece_y, board_x, board_y

def getPressTime(imgFilePath,deviceType='1920x1080',deleteImgFile = True):
      print('start getPressTime imgFilePath=%s,deviceType=%s,deleteImgFile=%s'%(imgFilePath,deviceType,deleteImgFile))
      im = Image.open(imgFilePath)
      config = open_accordant_config(screen_size=deviceType)
      # 获取棋子和 board 的位置
      piece_x, piece_y, board_x, board_y = find_piece_and_board(im,config)
      _press_time = calcPressTime(math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2),config)
      if (deleteImgFile==True):
          os.remove(imgFilePath)
          print('delete source file %s'%(imgFilePath))
      return _press_time

