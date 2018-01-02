# 教你用 Python 来玩微信跳一跳
## 游戏模式

> 2017 年 12 月 28 日下午，微信发布了 6.6.1 版本，加入了「小游戏」功能，并提供了官方 DEMO「跳一跳」。这是一个 2.5D 插画风格的益智游戏，玩家可以通过按压屏幕时间的长短来控制这个「小人」跳跃的距离。分数越高，那么在好友排行榜更加靠前。通过Python脚本自动运行，让你轻松霸榜。

![](https://ws1.sinaimg.cn/large/006tNc79ly1fn29l1ywd6g309o0eex6r.gif)

可能刚开始上手的时候，因为时间距离之间的关系把握不恰当，只能跳出几个就掉到了台子下面。
**如果能利用图像识别精确测量出起始和目标点之间测距离，就可以估计按压的时间来精确跳跃**

## 原理说明

1. 将手机点击到《跳一跳》小程序界面；

2. 用 ADB 工具获取当前手机截图，并用 ADB 将截图 pull 上来
```shell
adb shell screencap -p /sdcard/autojump.png
adb pull /sdcard/autojump.png .
```

3. 计算按压时间
  * 手动版：用 Matplotlib 显示截图，用鼠标先点击起始点位置，然后点击目标位置，计算像素距离；
  * 自动版：靠棋子的颜色来识别棋子，靠底色和方块的色差来识别棋盘；

4. 用 ADB 工具点击屏幕蓄力一跳；
```shell
adb shell input swipe x y x y time(ms)
```

## 使用教程

相关软件工具安装，和使用步骤请参考[Android 和 iOS 操作步骤](https://github.com/wangshub/wechat_jump_game/wiki/Android-%E5%92%8C-iOS-%E6%93%8D%E4%BD%9C%E6%AD%A5%E9%AA%A4)

## FAQ

> 请先查阅一下 issue 区，请按照issue模板正确提交问题

1. 如果你手机的的`config.json`出错导致弹跳不准确，或者有更好的参数？
    - 请在这里提交你的问题[issues/62](https://github.com/wangshub/wechat_jump_game/issues/62)，或者将参数PR给我们并附上你的最高成绩。

2. 如果你是 iOS，遇到问题怎么办？
    - 请移步参考：[issues/99](https://github.com/wangshub/wechat_jump_game/issues/99)和[issues/4](https://github.com/wangshub/wechat_jump_game/issues/4)

3. 如果你对环境安装和操作步骤不熟悉？
    - [Android 和 iOS 操作步骤](https://github.com/wangshub/wechat_jump_game/wiki/Android-%E5%92%8C-iOS-%E6%93%8D%E4%BD%9C%E6%AD%A5%E9%AA%A4)

4. 如果你的分数被微信清零或者排名不显示？
    - 注意不要刷太高分数，适当休息， 参见[issues/164](https://github.com/wangshub/wechat_jump_game/issues/164)

5. 如果有找不到`./autojump.png`文件的错误，
    - 请查阅[issue/194](https://github.com/wangshub/wechat_jump_game/issues/194)

6. 如果你在苦苦寻找视频教程？
    - 参考一位B站UP主的视频教程 [【微信跳一跳】教你如何不用双手还能霸占排行榜第一名](https://www.bilibili.com/video/av17796840/?redirectFrom=h5)

## QQ交流

- 314659953 (1000人 已满)

- 176740763 (500人 已满)

- 89213434  (2000人 已满)

- 64389940 (2000人)
