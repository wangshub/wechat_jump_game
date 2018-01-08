# -*- coding: utf-8 -*-
"""
手机屏幕截图的代码
"""
import subprocess
import os
import sys
from PIL import Image
import numpy as np
import cv2


# SCREENSHOT_WAY 是截图方法，经过 check_screenshot 后，会自动递减，不需手动修改
SCREENSHOT_WAY = 3


def pull_screenshot():
    """
    获取屏幕截图，目前有 0 1 2 3 四种方法，未来添加新的平台监测方法时，
    可根据效率及适用性由高到低排序
    """
    global SCREENSHOT_WAY
    if 1 <= SCREENSHOT_WAY <= 3:
        process = subprocess.Popen(
            'adb shell screencap -p',
            shell=True, stdout=subprocess.PIPE)
        binary_screenshot = process.stdout.read()
        if SCREENSHOT_WAY == 2:
            binary_screenshot = binary_screenshot.replace(b'\r\n', b'\n')
        elif SCREENSHOT_WAY == 1:
            binary_screenshot = binary_screenshot.replace(b'\r\r\n', b'\n')
        f = open('autojump.png', 'wb')
        f.write(binary_screenshot)
        f.close()

        # 将binary_screenshot直接转化为uint8数组，可直接用opencv的imdecode进行解码并读图图像，图像可以直接读入内存中，减少硬盘I/O。
        # 具体流程为捕获adb shell screencap -p的stdout，转化为uint8数组，用opencv的imdecode进行读取。
        # 如果脚本中用opencv处理图像的话，应该可以减少I/O的时间
        # 在我本机测试中，只有SCREENSHOT_WAY == 1时imdecode是正常的，其它情况matImage为空
        # 第一次用python，不是很熟悉
        rawArray = np.zeros(binary_screenshot.__len__(), dtype=np.uint8)
        for i in range(0, binary_screenshot.__len__()):
            rawArray[i] = binary_screenshot[i]
        matImage = cv2.imdecode(rawArray,cv2.IMREAD_COLOR)

        # 若imdecode失败，则matImage的类型为NoneType，成功则为nmupy.ndarry
        if isinstance(matImage,np.ndarray):
            cv2.imshow("1",matImage)
            cv2.waitKey()

    elif SCREENSHOT_WAY == 0:
        os.system('adb shell screencap -p /sdcard/autojump.png')
        os.system('adb pull /sdcard/autojump.png .')


def check_screenshot():
    """
    检查获取截图的方式
    """
    global SCREENSHOT_WAY
    if os.path.isfile('autojump.png'):
        try:
            os.remove('autojump.png')
        except Exception:
            pass
    if SCREENSHOT_WAY < 0:
        print('暂不支持当前设备')
        sys.exit()
    pull_screenshot()
    try:
        Image.open('./autojump.png').load()
        print('采用方式 {} 获取截图'.format(SCREENSHOT_WAY))
    except Exception:
        SCREENSHOT_WAY -= 1
        check_screenshot()


check_screenshot()
