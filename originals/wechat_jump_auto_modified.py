# coding: utf-8
'''
# === 思路 ===
# 核心：每次落稳之后截图，根据截图算出棋子的坐标和下一个块顶面的中点坐标，
#      根据两个点的距离乘以一个时间系数获得长按的时间
# 识别棋子：靠棋子的颜色来识别位置，通过截图发现最下面一行大概是一条直线，就从上往下一行一行遍历，
#      比较颜色（颜色用了一个区间来比较）找到最下面的那一行的所有点，然后求个中点，
#      求好之后再让 Y 轴坐标减小棋子底盘的一半高度从而得到中心点的坐标
# 识别棋盘：靠底色和方块的色差来做，从分数之下的位置开始，一行一行扫描，由于圆形的块最顶上是一条线，
#      方形的上面大概是一个点，所以就用类似识别棋子的做法多识别了几个点求中点，
#      这时候得到了块中点的 X 轴坐标，这时候假设现在棋子在当前块的中心，
#      根据一个通过截图获取的固定的角度来推出中点的 Y 坐标
# 最后：根据两点的坐标算距离乘以系数来获取长按时间（似乎可以直接用 X 轴距离）
'''
import os
import sys
import subprocess
import time
import math
from PIL import Image
import random
from six.moves import input

VERSION = "1.1.1"


# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


screenshot_way = 2

def check_screenshot():
	'''
	检查获取截图的方式
	'''
	global screenshot_way
	if os.path.isfile('autojump.png'):
		os.remove('autojump.png')
	if (screenshot_way < 0):
		print('暂不支持当前设备')
		sys.exit()
	pull_screenshot()
	try:
		Image.open('./autojump.png').load()
		print('Capture Method: {}'.format(screenshot_way))
	except Exception:
		screenshot_way -= 1
		check_screenshot()

def pull_screenshot():
	'''
	新的方法请根据效率及适用性由高到低排序
	'''
	global screenshot_way
	if screenshot_way == 2 or screenshot_way == 1:
		process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
		screenshot = process.stdout.read()
		if screenshot_way == 2:
			binary_screenshot = screenshot.replace(b'\r\n', b'\n')
		else:
			binary_screenshot = screenshot.replace(b'\r\r\n', b'\n')
		f = open('autojump.png', 'wb')
		f.write(binary_screenshot)
		f.close()
	elif screenshot_way == 0:
		os.system('adb shell screencap -p /sdcard/autojump.png')
		os.system('adb pull /sdcard/autojump.png .')


# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def set_button_position(im):
	'''
	将 swipe 设置为 `再来一局` 按钮的位置
	'''
	global swipe_x1, swipe_y1, swipe_x2, swipe_y2
	w, h = im.size
	left = int(w / 2)
	top = int(1584 * (h / 1920.0))
	left = int(random.uniform(left-50, left+50))
	top = int(random.uniform(top-10, top+10))    # 随机防 ban
	swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top


# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def find_piece_and_board(im):
	'''
	寻找关键坐标
	'''
	w, h = im.size #图片宽高
	im_pixel = im.load()


	scan_start_y = 0  # 扫描的起始 y 坐标
	# 以 50px 步长，尝试探测 scan_start_y
	for i in range((h-w)//2, h, 50):
		last_pixel = im_pixel[0, i]
		for j in range(1, w, 10):
			pixel = im_pixel[j, i]
			# 不是纯色的线，则记录 scan_start_y 的值，准备跳出循环
			if pixel[0] != last_pixel[0] or pixel[1] != last_pixel[1] or pixel[2] != last_pixel[2]:
				scan_start_y = i - 50
				break
		if scan_start_y:
			break
	print('scan_start_y: {}'.format(scan_start_y))

	def find_piece(pixel):
		return (50 < pixel[0] < 70) and (50 < pixel[1] < 70) and (90 < pixel[2] < 110)

	# 寻找棋子 ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆
	piece_base_height_1_2 = w//50

	# 粗查棋子位置
	piece_found,piece_tx,piece_ty = 0,0,0
	scan_piece_unit = w//40
	ny = (h+w)//2 #寻找下限 从画面中央的正方形的下缘开始
	while ny>scan_start_y and not piece_found:
		ny -= scan_piece_unit
		for nx in range(0,w,scan_piece_unit):
			pixel = im_pixel[nx,ny]
			if find_piece(pixel):
				piece_tx,piece_ty = nx,ny
				piece_found = True
				break
	print('piece_tx:%s | piece_ty:%s'%(piece_tx,piece_ty))
	if not all((piece_tx,piece_ty)): return 0, 0, 0, 0 #没找到棋子

	# 精查棋子位置
	piece_x,piece_y = 0,0
	piece_x_set = set()
	piece_width = w//14
	piece_height = w//5
	for ny in range(piece_ty+scan_piece_unit,piece_ty-piece_height,-1):
		for nx in range(max(piece_tx-piece_width,0),min(piece_tx+piece_width,w)):
			pixel = im_pixel[nx,ny]
			# print(nx,ny,pixel)
			if find_piece(pixel):
				piece_x_set.add(nx)
				piece_y = ny-piece_base_height_1_2 #上移棋子底盘高度的一半
		if piece_x_set:
			print(piece_x_set)
			piece_x = int(sum(piece_x_set)/len(piece_x_set))
			break
	print('piece_x:%s | piece_y:%s'%(piece_x,piece_y))


	# 寻找落点 ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆
	board_x,board_y = 0,0
	# 限制棋盘扫描的横坐标，避免音符 bug
	if piece_x < w/2:
		board_x_start,board_x_end = piece_x,w
	else:
		board_x_start,board_x_end = 0,piece_x

	# 寻找落点顶点
	for by in range((h-w)//2,(h+w)//2,2):
		bg_pixel = im_pixel[0, by]
		if board_x or board_y: break #找到了退出
		board_x_set = set()

		for bx in range(board_x_start, board_x_end):
			pixel = im_pixel[bx, by]
			# 修掉脑袋比下一个小格子还高的情况的 bug
			if abs(bx - piece_x) < piece_width*1.5: continue

			# 修掉圆顶的时候一条线导致的小 bug，这个颜色判断应该 OK，暂时不提出来
			if abs(pixel[0] - bg_pixel[0]) + abs(pixel[1] - bg_pixel[1]) + abs(pixel[2] - bg_pixel[2]) > 10:
				board_x_set.add(bx)
		if board_x_set:
			board_x = int(sum(board_x_set)/len(board_x_set))
	board_pixel = im_pixel[board_x, by]

	# 使用方法2 不用计算y点 所以以下部分可以省略

	# 从上顶点往下 +274 的位置开始向上找颜色与上顶点一样的点，为下顶点
	# 该方法对所有纯色平面和部分非纯色平面有效，对高尔夫草坪面、木纹桌面、药瓶和非菱形的碟机（好像是）会判断错误
	# board_max_height = int(w/2/120*70) #菱形宽高比为120:70
	# by2 = by #by2平台最下缘
	# for by2 in range(i+board_max_height, ny, -1): # 274 取开局时最大的方块的上下顶点距离
	# 	pixel = im_pixel[board_x, by2]
	# 	if abs(pixel[0] - board_pixel[0]) + abs(pixel[1] - board_pixel[1]) + abs(pixel[2] - board_pixel[2]) < 10:
	# 		break
	# board_y = (ny+by2)//2

	# 如果上一跳命中中间，则下个目标中心会出现 r245 g245 b245 的点，利用这个属性弥补上一段代码可能存在的判断错误
	# 若上一跳由于某种原因没有跳到正中间，而下一跳恰好有无法正确识别花纹，则有可能游戏失败，由于花纹面积通常比较大，失败概率较低
	# ty = 0 #target_y
	# for ty in range(ny, ny+board_max_height):
	# 	pixel = im_pixel[board_x, ty]
	# 	if abs(pixel[0] - 245) + abs(pixel[1] - 245) + abs(pixel[2] - 245) == 0:
	# 		board_y = ty+10
	# 		break

	# if not all((board_x, board_y)): return 0, 0, 0, 0

	return piece_x, piece_y, board_x, board_y



def jump(piece_x, piece_y, board_x, board_y,im):
	'''
	跳跃一定的距离
	'''
	# press_coefficient = 2.05
	# distance = math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2)
	# press_time = distance * press_coefficient
	# press_time = max(press_time, 200)   # 设置 200ms 是最小的按压时间
	# press_time = int(press_time)
	# print('distance:%s | time: %s'%(distance,press_time))

	# ========== 只判断x位移的跳跃算法 ==========
	distance2 = abs(board_x-piece_x)
	shortEdge = min(im.size)
	jumpLength = distance2/shortEdge
	press_coefficient = 1700 #720屏原系数为2多一点点 也就是距离为720需要1440ms 所以系数高一点点
	press_time = int(jumpLength*press_coefficient)
	print('jump:%.2f%% | time: %s'%(jumpLength*100,press_time))

	cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
		x1=swipe_x1,
		y1=swipe_y1,
		x2=swipe_x2,
		y2=swipe_y2,
		duration=press_time
	)
	print(cmd)
	os.system(cmd)
	return press_time


# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def main():
	check_screenshot() #检查截图

	count = 0
	i, next_rest, next_rest_time = 0, 1, 1
	while True:
		count += 1
		print('---\n%s | times: %s'%(int(time.time()),count))

		# 获取截图
		pull_screenshot()
		im = Image.open('./autojump.png')
		w,h = im.size
		if w>h: #添加图片方向判断
			im = im.rotate(-90,expand=True)
		# print('image | w:%s | h:%s'%(w,h))

		# 获取棋子和 board 的位置
		piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
		print(piece_x, piece_y, board_x, board_y)
		set_button_position(im) #随机点击位置
		jump(piece_x, piece_y, board_x, board_y,im)

		i += 1
		if i == next_rest:
			print('---\nJumped {} time，wait {}s'.format(i, next_rest_time))
			time.sleep(next_rest_time)
			print('\nContinue!')
			i, next_rest, next_rest_time = 0, random.randrange(10, 20), random.randrange(5, 10)
		time.sleep(random.uniform(1, 1.5)) #wait for jump finish


# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


if __name__ == '__main__':
	main()
