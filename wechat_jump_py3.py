# -*- coding: utf-8 -*-
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import re


android_fig_save_dir = '/sdcard/auto'  # Create 'auto' file in sdcard before start

def pull_screenshot():
    count = 0
    flag = 0
    while flag == 0 and count < 3:
        count += 1
        os.system('adb shell screencap -p %s/autojump.png' % android_fig_save_dir)
        files = os.popen('adb shell ls %s/' % android_fig_save_dir).read().splitlines()
        print files
        re_autojump = re.compile('autojump\\S{0,}')

        for file_ in files:
            if re_autojump.match(file_):
                print(file_)
                os.system('adb pull %s/%s autojump.png' % (android_fig_save_dir, file_))
                os.system('adb shell rm %s/%s' % (android_fig_save_dir, file_))
                flag=1
            else:
                os.system('adb shell rm %s/%s' % (android_fig_save_dir, file_))


def jump(distance):
    press_time = distance * 1.35
    press_time = int(press_time)
    cmd = 'adb shell input swipe 320 410 320 410 ' + str(press_time)
    print(cmd)
    os.system(cmd)


fig = plt.figure()


pull_screenshot()
img = np.array(Image.open('autojump.png'))
im = plt.imshow(img, animated=True)

update = True
click_count = 0
cor = []


def update_data():
    try:
        return np.array(Image.open('autojump.png'))
    except:
        return None


def updatefig(*args):
    global update
    if update:
        time.sleep(1.5)
        pull_screenshot()
        flag = update_data()
        if flag is None:
            pass
        else:
            im.set_array(flag)
            update = False
    return im,


def on_click(event):
    global update
    global ix, iy
    global click_count
    global cor

    ix, iy = event.xdata, event.ydata
    coords = [(ix, iy)]
    print('now = ', coords)
    cor.append(coords)

    click_count += 1
    if click_count > 1:
        click_count = 0
        cor1 = cor.pop()
        cor2 = cor.pop()

        distance = (cor1[0][0] - cor2[0][0])**2 + (cor1[0][1] - cor2[0][1])**2
        distance = distance ** 0.5
        print('distance = ', distance)
        jump(distance)
        update = True


fig.canvas.mpl_connect('button_press_event', on_click)
ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()
