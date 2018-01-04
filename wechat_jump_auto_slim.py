# coding: utf-8
import os,sys,subprocess,time,math,random
from PIL import Image

VERSION = "1.1.1"

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

screenshot_way = 2
# 检查获取截图的方式
def check_screenshot():
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

# 新的方法请根据效率及适用性由高到低排序
def pull_screenshot():
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

# 重设点击位置 再来一局位置
# 其实这个界面，应该是标准的9:16，然后fit当前窗体(600:800测试结果)。长窄屏可能需要特殊处理。
def set_button_position(im):
	global swipe_x1, swipe_y1, swipe_x2, swipe_y2
	w, h = im.size
	if h//16>w//9+2: #长窄屏 2px容差 获取ui描绘的高度
		uih = int(w/9*16)
	else:
		uih = h
	uiw = int(uih/16*9)
	left = int(w/2)
	top = int((h-uih)/2+uih*0.825) #根据9:16实测高度参数0.825
	left = int(random.uniform(left-uiw//5, left+uiw//5))
	top = int(random.uniform(top-uih//28, top+uih//28))    # 随机防 ban
	swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

# 寻找起点和终点坐标
def find_piece_and_board(im):
	w, h = im.size #图片宽高
	im_pixel = im.load()

	def find_piece(pixel):
		return (40 < pixel[0] < 65) and (40 < pixel[1] < 65) and (80 < pixel[2] < 105)

	# 寻找棋子 ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

	# 粗查棋子位置
	piece_found,piece_fx,piece_fy = 0,0,0
	scan_piece_unit = w//40 #间隔单位
	ny = (h+w)//2 #寻找下限 从画面中央的正方形的下缘开始
	while ny>(h-w)//2 and not piece_found:
		ny -= scan_piece_unit
		for nx in range(0,w,scan_piece_unit):
			pixel = im_pixel[nx,ny]
			if find_piece(pixel):
				piece_fx,piece_fy = nx,ny
				piece_found = True
				break
	print('%-12s %s,%s'%('piece_fuzzy:',piece_fx,piece_fy))
	if not piece_fx: return 0, 0 #没找到棋子

	# 精查棋子位置
	piece_x = 0
	piece_x_set = set()
	piece_width = w//14 #估算棋子宽度
	piece_height = w//5 #估算棋子高度
	for ny in range(piece_fy+scan_piece_unit,piece_fy-piece_height,-4):
		for nx in range(max(piece_fx-piece_width,0),min(piece_fx+piece_width,w)):
			pixel = im_pixel[nx,ny]
			# print(nx,ny,pixel)
			if find_piece(pixel):
				piece_x_set.add(nx)
		if len(piece_x_set)>10:
			piece_x = sum(piece_x_set)/len(piece_x_set)
			break
	print('%-12s %s'%('p_exact_x:',piece_x))

	# 寻找落点 ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆
	board_x = 0
	# 限制棋盘扫描的横坐标，避免音符 bug
	if piece_x < w/2:
		board_x_start,board_x_end = round(piece_x),w
	else:
		board_x_start,board_x_end = 0,round(piece_x)

	# 寻找落点顶点
	for by in range((h-w)//2,(h+w)//2,4):
		bg_pixel = im_pixel[0, by]
		board_x_set = set()
		for bx in range(board_x_start, board_x_end):
			pixel = im_pixel[bx, by]
			# 修掉脑袋比下一个小格子还高的情况 屏蔽小人左右的范围
			if abs(bx - piece_x) < piece_width*1.5: continue

			# 修掉圆顶的时候一条线导致的小 bug，这个颜色判断应该 OK，暂时不提出来
			if abs(pixel[0]-bg_pixel[0]) + abs(pixel[1]-bg_pixel[1]) + abs(pixel[2]-bg_pixel[2]) > 10:
				board_x_set.add(bx)

		if len(board_x_set)>10:
			board_x = sum(board_x_set)/len(board_x_set)
			print('%-12s %s'%('target_x:',board_x))
			break #找到了退出

	return piece_x, board_x

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

def jump(piece_x, board_x,im):
	distanceX = abs(board_x-piece_x)
	shortEdge = min(im.size)
	jumpLength = distanceX/shortEdge
	press_coefficient = 1700 #跳过整个宽度 需要按压的毫秒数
	press_time = round(jumpLength*press_coefficient)
	print('%-12s %.2f%% (%s/%s) | Press: %sms'%('Distance:',jumpLength*100,distanceX,shortEdge,press_time))

	cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
		x1=swipe_x1,
		y1=swipe_y1,
		x2=swipe_x2,
		y2=swipe_y2,
		duration=press_time
	)
	# print(cmd)
	os.system(cmd)
	return press_time

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

def main():
	check_screenshot() #检查截图

	count = 0
	i, next_rest, next_rest_time = 0, 1, 1
	while True:
		count += 1
		print('---\n%-12s %s (%s)'%('Times:',count,int(time.time())))

		# 获取截图
		pull_screenshot()
		im = Image.open('./autojump.png')
		w,h = im.size
		if w>h: #添加图片方向判断
			im = im.rotate(-90,expand=True)
		# print('image | w:%s | h:%s'%(w,h))

		# 获取棋子和 board 的位置
		piece_x, board_x = find_piece_and_board(im)
		set_button_position(im) #随机点击位置
		jump(piece_x, board_x,im)

		i += 1
		if i == next_rest:
			print('---\nJumped {} time，wait {} s...'.format(i, next_rest_time))
			time.sleep(next_rest_time)
			print('Continue!')
			i, next_rest, next_rest_time = 0, random.randrange(10, 20), random.randrange(5, 10)
		time.sleep(random.uniform(1, 1.5)) #wait for jump finish

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

if __name__ == '__main__':
	main()
