# 教你用Python来玩微信跳一跳

[https://wangshub.github.io](https://wangshub.github.io)

[github项目地址](https://github.com/wangshub/wechat_jump_game)
########设计思路##########
原作者的项目地址见上方。
开挂就没有了游戏乐趣，也破坏了游戏的公平性。但写挂是程序员的乐趣，这只是原作者写的小玩具，忘诸位理解。
这里讲讲此”外挂“的思路：
先给电脑安装adb驱动，连上手机，打开开发者usb调试，通过adb截屏并pull到电脑上，用matplotlib，结合各自手机的屏幕参数取出棋子中心点和目标跳台中心点坐标，并计算两点距离。
再根据该距离以及各自手机的按压时间系数，算出按压屏幕的时间，通过adb工具模拟人手对手机屏幕按压。每跳到一个新位置，自动截屏传给电脑分析。至于怎么识别手机屏幕上的各种跳台，
作者好像是通过截取多张图片，用opencv库进行图像识别，已经训练好了，我们不用管了。对于这一点，需要提醒的是，如果你的手机有悬浮球，记得关了，我之前就是因为没关，导致经常失败，
计算机把悬浮球当成了目标。。。
我们只需要修改config.json里的参数即可，根据不同手机参数需要调整，issue区里面有很多配置好的参数，可以参考。
安装adb驱动后记得配置环境变量，因为你的控制台程序是在你的python代码所在目录下运行的。还有些手机，adb devices找不到设备，那是你手机的问题，需要在你电脑端用户文件夹/.android下配置adb_usb.ini
文件，具体操作，根据自己的机型自行百度。



* QQ群
    * github微信跳一跳    **314659953**(已满)
    * github微信跳一跳(2) **176740763**

### **更新日志：**

* 2017-12-29 ：
  * 增加更新自动化运行脚本，感谢github上的 [@binderclip](https://github.com/binderclip)

* 2017-12-30 :
  * 请将安卓手机的usb调试模式打开，设置》更多设置》开发者选项》USB调试，如果出现运行脚本后小人不跳的情况，请检查是否有打开“USB调试（安全模式）”
  * 根据大家反馈：1080屏幕距离系数**1.393**，2k屏幕为**1**
  * 添加部分机型配置文件，可直接复制使用



### 相关问题

> 请先查阅一下issue区

- 参数出错请在这里提交：[issues/62](https://github.com/wangshub/wechat_jump_game/issues/62)
- 如果你是ios参考一下： [issues/99](https://github.com/wangshub/wechat_jump_game/issues/99) 和
[/issues/4](https://github.com/wangshub/wechat_jump_game/issues/4)
- 如果你想自动运行：请运行`wechat_jump_auto.py`，记得修改`/config/default.json`参数（这个是默认的配置）
- 如果你是ios，请运行：`wechat_jump_iOS_py3.py`
- 更新了一些分辨率参数配置，请按照你的手机分辨率从`config/`文件夹找到相应的配置，拷贝到*.py同级目录;（如果屏幕分辨率能成功探测，会直接调用config目录的配置，不需要复制）
- 注意：别刷太高，已经有同学遇到分数清零的情况了[164](https://github.com/wangshub/wechat_jump_game/issues/164)
- 如果有找不到`./autojump.png`图片的错误，请查阅[194](https://github.com/wangshub/wechat_jump_game/issues/194)

## 游戏模式

> 2017年12月28日下午，微信发布了 6.6.1 版本，加入了「小游戏」功能，并提供了官方 demo「跳一跳」。

这是一个 2.5D 插画风格的益智游戏，玩家可以通过按压屏幕时间的长短来控制这个「小人」跳跃的距离。可能刚开始上手的时候，因为时间距离之间的关系把握不恰当，只能跳出几个就掉到了台子下面。
玩法类似于《flappy bird》

![](https://ws1.sinaimg.cn/large/c3a916a7gy1fmxe4gnfhnj20hs0a0t8q.jpg)

**如果能精确测量出起始和目标点之间测距离，就可以估计按压的时间来精确跳跃？所以花2个小时写了一个python脚本进行验证**

希望不要把分数刷太高，容易没朋友的。。。

## 工具介绍

- Python
- 手机或模拟器
- [Adb](https://developer.android.com/studio/releases/platform-tools.html) 驱动，可以到[这里](https://adb.clockworkmod.com/)下载
- 相关依赖

如果你是`iOS`，请参考下面的配置：
- 使用真机调试wda，参考iOS 真机如何安装 [WebDriverAgent · TesterHome](https://testerhome.com/topics/7220)
- 安装[openatx/facebook-wda](https://github.com/openatx/facebook-wda)
- Python 3

## 依赖安装

``` bash
    pip install -r requirements.txt
```

## 原理说明

1. 将手机点击到《跳一跳》小程序界面；
2. 用Adb 工具获取当前手机截图，并用adb将截图pull上来

```shell
    adb shell screencap -p /sdcard/autojump.png
    adb pull /sdcard/autojump.png .
```

3. 计算按压时间
  * 手动版：用matplotlib显示截图，用鼠标点击起始点和目标位置，计算像素距离；
  * 自动版：靠棋子的颜色来识别棋子，靠底色和方块的色差来识别棋盘；

5. 用Adb工具点击屏幕蓄力一跳；

```shell
    adb shell input swipe x y x y time(ms)
```


## 安卓手机操作步骤

- 安卓手机打开USB调试，设置》开发者选项》USB调试
- 电脑与手机USB线连接，确保执行`adb devices`可以找到设备id
- 界面转至微信跳一跳游戏，点击开始游戏
- 运行`python wechat_jump_auto.py`，如果手机界面显示USB授权，请点击确认


## IOS手机操作步骤

1. 运行安装好的 `WebDriverAgentRunner`
2. 将手机点击到《跳一跳》小程序界面
3. 运行脚本。有两种模式可供选择：手动辅助跳 和 自动连续跳
    * 手动辅助跳
        * 命令行运行`python3 wechat_jump_iOS_py3.py`
        * 依次点击弹出的窗口中的起始位置和目标位置，会自动计算距离后起跳
        * 根据起跳的精准情况更改 `python3 wechat_jump_iOS_py3.py` 中的 `time_coefficient`参数，直到获得最佳取值
    * 自动连续跳
        * 拷贝`./config/iPhone`目录下对应的设备配置文件，重命名并替换到`./config.json`
        * 命令行运行`python3 wechat_jump_auto_iOS.py`
        * 会自动计算坐标并连续起跳，根据起跳的精准情况更改 `./config.json` 中的 `press_coefficient`参数，直到获得最佳取值

## 实验结果

![](https://ws1.sinaimg.cn/large/c3a916a7gy1fmxel5dkxvj20u01hcmzx.jpg)

## TODO

- [x] 可以对拉上来的图片进行颜色分割，识别小人和目标中心，这样就不需要手动点击自动弹跳。

> 事实证明，机器人比人更会玩儿游戏。
