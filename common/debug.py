# -*- coding: utf-8 -*-
"""
这儿是debug的代码，当DEBUG_SWITCH开关开启的时候，会将各种信息存在本地，方便检查故障
"""
import os
import sys
import shutil
import math
from PIL import ImageDraw
from common import ai

from common import adb

screenshot_backup_dir = 'screenshot_backups/'


def make_debug_dir(screenshot_backup_dir):
    """
    创建备份文件夹
    """
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)


def backup_screenshot(ts):
    """
    为了方便失败的时候 debug
    """
    make_debug_dir(screenshot_backup_dir)
    shutil.copy('autojump.png', '{}{}.png'.format(screenshot_backup_dir, ts))


def save_debug_screenshot(ts, im, piece_x, piece_y, board_x, board_y, debugtype = 'auto'):
    """
    对 debug 图片加上详细的注释
    
    """
    make_debug_dir(screenshot_backup_dir)
    draw = ImageDraw.Draw(im)
    draw.line((piece_x, piece_y) + (board_x, board_y), fill=2, width=3)
    draw.line((piece_x, 0, piece_x, im.size[1]), fill=(255, 0, 0))
    draw.line((0, piece_y, im.size[0], piece_y), fill=(255, 0, 0))
    draw.line((board_x, 0, board_x, im.size[1]), fill=(0, 0, 255))
    draw.line((0, board_y, im.size[0], board_y), fill=(0, 0, 255))
    draw.ellipse((piece_x - 10, piece_y - 10, piece_x + 10, piece_y + 10), fill=(255, 0, 0))
    draw.ellipse((board_x - 10, board_y - 10, board_x + 10, board_y + 10), fill=(0, 0, 255))
    del draw
    im.save('{}{}_{}.png'.format(screenshot_backup_dir, ts, debugtype))

def computing_error(last_press_time, target_board_x, target_board_y, last_piece_x, last_piece_y, temp_piece_x, temp_piece_y):
    '''
    计算跳跃实际误差
    '''
    target_distance = math.sqrt((target_board_x - last_piece_x) ** 2 + (target_board_y - last_piece_y) ** 2)  # 上一轮目标跳跃距离
    actual_distance = math.sqrt((temp_piece_x - last_piece_x) ** 2 + (temp_piece_y - last_piece_y) ** 2)  # 上一轮实际跳跃距离
    jump_error_value = math.sqrt((target_board_x - temp_piece_x) ** 2 + (target_board_y - temp_piece_y) ** 2)  # 跳跃误差

    print(round(target_distance), round(jump_error_value), round(actual_distance), round(last_press_time))
    # 将结果采集进学习字典
    if last_piece_x > 0 and last_press_time > 0:
        ai.add_data(round(actual_distance, 2), round(last_press_time))
        # print(round(actual_distance), round(last_press_time))

def dump_device_info():
    """
    显示设备信息
    """
    size_str = adb.run('shell wm size')
    device_str = adb.run('shell getprop ro.product.device')
    phone_os_str = adb.run('shell getprop ro.build.version.release')
    density_str = adb.run('shell wm density')
    print("""**********
Screen: {size}
Density: {dpi}
Device: {device}
Phone OS: {phone_os}
Host OS: {host_os}
Python: {python}
**********""".format(
        size=size_str.strip(),
        dpi=density_str.strip(),
        device=device_str.strip(),
        phone_os=phone_os_str.strip(),
        host_os=sys.platform,
        python=sys.version
    ))
