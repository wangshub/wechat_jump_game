import wda
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import math
import time
import os

# 截图距离 * time_coefficient = 按键时长
# 此数据是 iPhoneSE 的推荐系数，可根据手机型号进行调整
time_coefficient = 0.00225

c = wda.Client()
s = c.session()

# 截屏并保存
def pull_screenshot(filename):
    c.screenshot(filename)

# 跳
def jump(distance):
    press_time = distance * time_coefficient
    print('按压时间:', press_time)
    s.tap_hold(200,200,press_time)


# 初始化图像
def initFigure():
    pull_screenshot('screen.png')
    return plt.imshow(np.array(Image.open('screen.png')), animated=True)

# 更新图像
def updateFigure(*args):
    global im

    pull_screenshot('screen.png')
    im.set_array(np.array(Image.open('screen.png')))


# 坐标数组
coords = []

# 鼠标点击事件
def onClick(event):
    global coords

    # 提取坐标
    ix, iy = event.xdata, event.ydata
    coords.append((ix, iy))
    print('now = ', (ix, iy))


    if len(coords) == 2:
        cor1 = coords.pop()
        cor2 = coords.pop()

        distance = (cor1[0] - cor2[0])**2 + (cor1[1] - cor2[1])**2
        distance = distance ** 0.5
        print('distance = ', distance)
        jump(distance)


fig = plt.figure()

im = initFigure()

# 绑定事件
fig.canvas.mpl_connect('button_press_event', onClick)

# 设置更新函数
ani = animation.FuncAnimation(fig, updateFigure, interval=50, blit=False)


plt.show()


