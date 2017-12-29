#-*- coding=utf8 -*-
import cv2  
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

img = cv2.imread('pic/5.jpg')  
# gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)                        #转换为灰度图像
gray = np.mat(img[:, :, 0])


x_range = [0,1080]
y_range = [720, 1000]

for y in range(min(y_range), max(y_range)):
    pass

plt.imshow(gray, cmap='gray')
plt.show()
















# # ret, binary = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)        #转换为二值图像
# ret,binary = cv2.threshold(gray,127,255,0)

# _,contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)#提取轮廓

# cv2.drawContours(img,contours,-1,(0,0,255),2)  

# # print contours
# # cv2.imshow("img", img)  
# # cv2.waitKey(0)
# # plt.subplot(221)
# plt.imshow(gray, cmap='gray')

# # plt.subplot(222)
# # plt.imshow(img, cmap='gray')

# # plt.subplot(223)
# # plt.imshow(binary, cmap='gray')

# plt.show()