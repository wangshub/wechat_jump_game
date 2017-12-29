#encoding:utf-8
#黄色检测
import numpy as np
import argparse
import cv2
import scipy.misc

image = cv2.imread('2.png')
color = [
    ([0, 70, 70], [100, 255, 255])#黄色范围~这个是我自己试验的范围，可根据实际情况自行调整~注意：数值按[b,g,r]排布
]
#如果color中定义了几种颜色区间，都可以分割出来 
for (lower, upper) in color:
    # 创建NumPy数组
    lower = np.array(lower, dtype = "uint8")#颜色下限
    upper = np.array(upper, dtype = "uint8")#颜色上限

    # 根据阈值找到对应颜色
    mask = cv2.inRange(image, lower, upper)
    output = cv2.bitwise_and(image, image, mask = mask)
    

    scipy.misc.imsave('outfile.jpg', output)
    # 展示图片
    # cv2.imshow("images", np.hstack([image, output]))
    # cv2.waitKey(0)