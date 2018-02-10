# -*- coding: utf-8 -*-
"""
手机屏幕截图的代码
"""
import subprocess
import os
import sys
from PIL import Image

from common import adb

# SCREEN_SHOT_WAY 是截图方法，经过 check_screen_shot 后，会自动递减，不需手动修改
SCREEN_SHOT_WAY = 3


def pull_screen_shot():
    """
    获取屏幕截图，目前有 0 1 2 3 四种方法，未来添加新的平台监测方法时，
    可根据效率及适用性由高到低排序
    """
    global SCREEN_SHOT_WAY
    if 1 <= SCREEN_SHOT_WAY <= 3:
        process = subprocess.Popen(
            adb.adb_path + ' shell screencap -p',
            shell=True, stdout=subprocess.PIPE)
        binary_screen_shot = process.stdout.read()
        if SCREEN_SHOT_WAY == 2:
            binary_screen_shot = binary_screen_shot.replace(b'\r\n', b'\n')
        elif SCREEN_SHOT_WAY == 1:
            binary_screen_shot = binary_screen_shot.replace(b'\r\r\n', b'\n')
        f = open('auto_jump.png', 'wb')
        f.write(binary_screen_shot)
        f.close()
    elif SCREEN_SHOT_WAY == 0:
        adb.run('shell screencap -p /sdcard/auto_jump.png')
        adb.run('pull /sdcard/auto_jump.png .')


def check_screen_shot():
    """
    检查获取截图的方式
    """
    global SCREEN_SHOT_WAY
    if os.path.isfile('auto_jump.png'):
        try:
            os.remove('auto_jump.png')
        except Exception as e:
            print('check_screen_shot Exception {}'.format(e))
            pass
    if SCREEN_SHOT_WAY < 0:
        print('暂不支持当前设备')
        sys.exit()
    pull_screen_shot()
    try:
        Image.open('./auto_jump.png').load()
        print('采用方式 {} 获取截图'.format(SCREEN_SHOT_WAY))
    except Exception as e:
        print('check_screen_shot Exception {}'.format(e))
        SCREEN_SHOT_WAY -= 1
        check_screen_shot()
