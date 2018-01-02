# coding: utf-8
'''
默认PEP8的docstring，文件注释写在这里
'''
import os
import sys
import shutil
from PIL import ImageDraw

screenshot_backup_dir = 'screenshot_backups/'


def make_debug_dir(screenshot_backup_dir):
    '''
    创建备份文件夹
    '''
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)


def backup_screenshot(ts):
    '''
    为了方便失败的时候 debug
    '''
    make_debug_dir(screenshot_backup_dir)
    shutil.copy('autojump.png', '{}{}.png'.format(screenshot_backup_dir, ts))


def save_debug_screenshot(ts, im, piece_x, piece_y, board_x, board_y):
    '''
    对 debug 图片加上详细的注释
    '''
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
    im.save('{}{}_d.png'.format(screenshot_backup_dir, ts))


def dump_device_info():
    '''
    显示设备信息
    '''
    size_str = os.popen('adb shell wm size').read()
    device_str = os.popen('adb shell getprop ro.product.model').read()
    density_str = os.popen('adb shell wm density').read()
    print("""**********
Screen: {size}
Density: {dpi}
DeviceType: {type}
OS: {os}
Python: {python}
**********""".format(
        size=size_str.strip(),
        type=device_str.strip(),
        dpi=density_str.strip(),
        os=sys.platform,
        python=sys.version
    ))
