import wda
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import math
import time
import os

# 截图距离 * time_coefficient = 按键时长
# 此数据是 iPhoneX 的推荐系数，可根据手机型号进行调整
time_coefficient = 0.00125

c = wda.Client()
s = c.session()

def pull_screenshot():
    c.screenshot('autojump.png')

def jump(distance):
    press_time = distance * time_coefficient
    press_time = press_time
    print(press_time)
    s.tap_hold(200,200,press_time)

fig = plt.figure()
index = 0
cor = [0, 0]
pull_screenshot()
img = np.array(Image.open('autojump.png'))

update = True
click_count = 0
cor = []

def update_data():
    return np.array(Image.open('autojump.png'))

im = plt.imshow(img, animated=True)

def updatefig(*args):
    global update
    if update:
        time.sleep(1)
        pull_screenshot()
        im.set_array(update_data())
        update = False
    return im,

def onClick(event):
    global update
    global ix, iy
    global click_count
    global cor

    # next screenshot
    ix, iy = event.xdata, event.ydata
    coords = []
    coords.append((ix, iy))
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

fig.canvas.mpl_connect('button_press_event', onClick)
ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()


