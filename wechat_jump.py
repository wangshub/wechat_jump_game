# -*- coding: utf-8 -*-
from __future__ import print_function, division
import os
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cv2

scale = 0.25

template = cv2.imread('./resource/image/character.png')
template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
template_size = template.shape[:2]


def search(img):
    result = cv2.matchTemplate(img, template, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    cv2.rectangle(
        img,
        (min_loc[0], min_loc[1]),
        (min_loc[0] + template_size[1], min_loc[1] + template_size[0]),
        (255, 0, 0),
        4)
    return img, min_loc[0] + template_size[1] / 2, min_loc[1] +  template_size[0]


def pull_screenshot():
    filename = datetime.datetime.now().strftime("%H%M%S") + '.png'
    os.system('mv autojump.png {}'.format(filename))
    os.system('adb shell screencap -p /sdcard/autojump.png')
    os.system('adb pull /sdcard/autojump.png ./autojump.png')


def jump(distance):
    press_time = distance * 1.35
    press_time = int(press_time)
    cmd = 'adb shell input swipe 320 410 320 410 ' + str(press_time)
    print(cmd)
    os.system(cmd)


def update_data():
    global src_x, src_y

    img = cv2.imread('./autojump.png')
    img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
    img, src_x, src_y = search(img)
    return img


fig = plt.figure()
pull_screenshot()
img = update_data()
im = plt.imshow(img, animated=True)

update = True


def updatefig(*args):
    global update

    if update:
        time.sleep(1)
        pull_screenshot()
        im.set_array(update_data())
        update = False
    return im,


def on_click(event):
    global update    
    global src_x, src_y
    
    dst_x, dst_y = event.xdata, event.ydata

    distance = (dst_x - src_x)**2 + (dst_y - src_y)**2 
    distance = (distance ** 0.5) / scale
    print('distance = ', distance)
    jump(distance)
    update = True


fig.canvas.mpl_connect('button_press_event', on_click)
ani = animation.FuncAnimation(fig, updatefig, interval=5, blit=True)
plt.show()
