# -*-coding:utf8-*-#
__author__ = 'play4fun'
"""
create time:15-10-25 下午12:09

任何一副灰度图像 可以 看成拓扑平面
灰度值 的区域可以 看成是 山峰 
灰度值低的区域可以 看成是山谷。
我们向每一个山谷中灌不同颜色的水。随着水的位的升  不同山谷的水就会相遇汇合 
为了防止不同山 的水 汇合 我们需要在水汇合的地方构建 堤坝。不停的灌水 不停的构建堤坝
直到所有的山峰都被水淹没。
我们构建好的堤坝就是对图像的分割。 
这就是分水岭算法的背后哲理。

每一次灌水 我们的标签就会 更新 当两个不同 色的标签相 时就构建堤 坝 直到将所有山峰淹没 最后我们得到的 界对  堤坝 的值为 -1

"""

import numpy as np
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('1.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
cv2.imshow('thresh', thresh)

# noise removal
kernel = np.ones((3, 3), np.uint8)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

# sure background area
sure_bg = cv2.dilate(opening, kernel, iterations=3)
# Finding sure foreground area
# 距离变换的基本含义是计算一个图像中非像素点到最近的零像素点的距离
# 也就是到零像素点的最短距离
# 个最常见的距离变换算法就是通过连续的腐蚀操作来实现,
# 腐蚀操作的停止条件是所有前景像素都被完全腐蚀。
# 这样根据腐蚀的先后顺序，我们就得到各个前景像素点到前景中心骨架像素点的距离
# 根据各个像素点的距离值，设置为不同的灰度值。这样就完成了二值图像的距离变换
# cv2.distanceTransform(src, distanceType, maskSize)
# 第二个参数 0,1,2 分别 示 CV_DIST_L1, CV_DIST_L2 , CV_DIST_C
dist_transform = cv2.distanceTransform(opening, 1, 5)
ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)#图像相减
cv2.imshow('unknown', unknown)
# 边界

# 腐蚀


# Marker labelling创建标签
ret, markers1 = cv2.connectedComponents(sure_fg)
# Add one to all labels so that sure background is not 0, but 1
# 把将背景标 为 0 其他的对 使用从 1 开始的正整数标
markers = markers1 + 1
# Now, mark the region of unknown with zero
markers[unknown == 255] = 0

# cv2.imshow('markers', markers1)

# 到最后一步 实施分水岭算法了。标签图像将会 修 改  界区域的标 将变为 -1
markers3 = cv2.watershed(img, markers)
img[markers3 == -1] = [255, 0, 0]

cv2.imshow('watershed', img)
cv2.waitKey(0)
cv2.destroyAllWindows()