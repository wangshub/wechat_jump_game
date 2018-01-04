# 教你用 Python 来玩微信跳一跳
## 游戏模式

> 2017 年 12 月 28 日下午，微信发布了 6.6.1 版本，加入了「小游戏」功能，并提供了官方 DEMO「跳一跳」。这是一个 2.5D 插画风格的益智游戏，玩家可以通过按压屏幕时间的长短来控制这个「小人」跳跃的距离。分数越高，那么在好友排行榜更加靠前。通过 Python 脚本自动运行，让你轻松霸榜。

![](./resource/image/jump.gif)

可能刚开始上手的时候，因为时间距离之间的关系把握不恰当，只能跳出几个就掉到了台子下面。**如果能利用图像识别精确测量出起始和目标点之间测距离，就可以估计按压的时间来精确跳跃。**

## 原理说明

1. 将手机点击到《跳一跳》小程序界面

2. 用 ADB 工具获取当前手机截图，并用 ADB 将截图 pull 上来
```shell
adb shell screencap -p /sdcard/autojump.png
adb pull /sdcard/autojump.png .
```

3. 计算按压时间
  * 手动版：用 Matplotlib 显示截图，用鼠标先点击起始点位置，然后点击目标位置，计算像素距离；
  * 自动版：靠棋子的颜色来识别棋子，靠底色和方块的色差来识别棋盘；

4. 用 ADB 工具点击屏幕蓄力一跳
```shell
adb shell input swipe x y x y time(ms)
```

## 使用教程

- 方法 1：使用 app 进行一键操作。目前已适配 Win10 64位/macOS 平台 Android 一键操作，下载请移步 [STOP_jump](https://github.com/wangshub/wechat_jump_game/releases)

- 方法 2：相关软件工具安装和使用步骤请参考 [Android 和 iOS 操作步骤](https://github.com/wangshub/wechat_jump_game/wiki/Android-%E5%92%8C-iOS-%E6%93%8D%E4%BD%9C%E6%AD%A5%E9%AA%A4)

## FAQ

- 详见 [Wiki-FAQ](https://github.com/wangshub/wechat_jump_game/wiki/FAQ)

## 更新日志

- 详见 [changelog](https://github.com/wangshub/wechat_jump_game/blob/master/changelog.md)

## 开发者列表

- 详见 [contributors](https://github.com/wangshub/wechat_jump_game/graphs/contributors)

## QQ 交流

- 314659953 (1000人 已满)
- 176740763 (500人 已满)
- 89213434 (2000人 已满)
- 64389940 (2000人)
