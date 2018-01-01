# 教你用 Python 来玩微信跳一跳

[https://wangshub.github.io](https://wangshub.github.io)

[GitHub 项目地址](https://github.com/wangshub/wechat_jump_game)

* QQ 群
    * github微信跳一跳    **314659953**(已满)
    * github微信跳一跳(2) **176740763**（满）
    * 跳一跳 **89213434**

### **更新日志：**

* 2017-12-29 ：
  * 增加更新自动化运行脚本，感谢 GitHub 上的[@binderclip](https://github.com/binderclip)

* 2017-12-30 :
  * 请将安卓手机的 USB 调试模式打开，设置》更多设置》开发者选项》USB 调试，如果出现运行脚本后小人不跳的情况，请检查是否有打开“USB 调试（安全模式）”
  * 根据大家反馈：1080 屏幕距离系数 **1.393**，2K 屏幕为 **1**
  * 添加部分机型配置文件，可直接复制使用



### 相关问题

> 请先查阅一下 issue 区

- 参数出错请在这里提交：[issues/62](https://github.com/wangshub/wechat_jump_game/issues/62)
- iOS 相关问题：[issues/99](https://github.com/wangshub/wechat_jump_game/issues/99) 和
[/issues/4](https://github.com/wangshub/wechat_jump_game/issues/4)
- [iOS 苹果手机操作步骤](#ios-%E6%89%8B%E6%9C%BA%E6%93%8D%E4%BD%9C%E6%AD%A5%E9%AA%A4)
- [Android 安卓手机操作步骤](#%E5%AE%89%E5%8D%93%E6%89%8B%E6%9C%BA%E6%93%8D%E4%BD%9C%E6%AD%A5%E9%AA%A4)
- 注意：别刷太高，已经有同学遇到分数清零的情况了[164](https://github.com/wangshub/wechat_jump_game/issues/164)
- 如果有找不到`./autojump.png`图片的错误，请查阅[194](https://github.com/wangshub/wechat_jump_game/issues/194)
- 小白用户可以参考一个B站UP主的视频教程 [【微信跳一跳】教你如何不用双手还能霸占排行榜第一名](https://www.bilibili.com/video/av17796840/?redirectFrom=h5)

## 游戏模式

> 2017 年 12 月 28 日下午，微信发布了 6.6.1 版本，加入了「小游戏」功能，并提供了官方 DEMO「跳一跳」。

这是一个 2.5D 插画风格的益智游戏，玩家可以通过按压屏幕时间的长短来控制这个「小人」跳跃的距离。可能刚开始上手的时候，因为时间距离之间的关系把握不恰当，只能跳出几个就掉到了台子下面。
玩法类似于《Flappy Bird》

![](https://ws1.sinaimg.cn/large/c3a916a7gy1fmxe4gnfhnj20hs0a0t8q.jpg)

**如果能精确测量出起始和目标点之间测距离，就可以估计按压的时间来精确跳跃？所以花 2 个小时写了一个 Python 脚本进行验证**

希望不要把分数刷太高，容易没朋友的。。。

## 操作规范
> 考虑到生产环境的规范性，实验与项目之间不受干扰，请尽量用新的虚拟环境来完成实验

MacOS/Win,请使用如下操作开辟新的虚拟环境（不强调表示MacOS/Win相同操作）
- 下载Anaconda. MacOS:默认安装/Win:注意安装时候勾选配置路径或者之后手动配置，直至cmd后conda关键字有效
- 查看所有的虚拟环境`conda info --envs`
- 使用命令：`conda create -n wechat_env python=3`，创建名为`wechat_env`的虚拟环境，且配置python版本为python3
- 激活虚拟环境：MacOS: `source activate wechat_env`/Win：`activate wechat_env`
- 安装所需要的包，比如`matplotlib`等，建议使用`conda install package_name`来避免虚拟环境包的路径问题

**接下来的操作非必须，仅当实验完成后可操作，试验阶段全程在虚拟环境中操作，进入虚拟环境会有前置符号表示如：**
```
(wechat_env) ~/Desktop/wechat_jump_game-master>
```
- 退出虚拟环境：MacOS: `source deactivate wechat_env` / Win: `deactivate wecha_env`
- 删除虚拟环境： `conda remove -n wechat_env --all`


## 工具介绍

- Python
- 手机或模拟器
- [ADB](https://developer.android.com/studio/releases/platform-tools.html) 驱动，可以到[这里](https://adb.clockworkmod.com/)下载
- 相关依赖

如果你是`iOS` + MacOS，请参考下面的配置：
- 使用真机调试 WDA，参考 iOS 真机如何安装[WebDriverAgent · TesterHome](https://testerhome.com/topics/7220)
- 安装[openatx/facebook-wda](https://github.com/openatx/facebook-wda)
- Python 3

如果你是 `Android` + MacOS，请参考下面的配置：
- Python 3
- 使用brew进行安装 `brew cask install android-platform-tools`
- 安装完后插入安卓设备且安卓已打开usb调试模式（部分新机型可能需要再另外勾上 允许模拟点击 权限），终端输入 `adb devices` ,显示如下表明设备已连接
```
List of devices attached
6934dc33	device
```

如果你是 `Android` + Windows，请参考下面的配置：
- Python 3
- 安装 [ADB](https://adb.clockworkmod.com/) 后，请在 环境变量 里将 adb 的安装路径保存到 PATH 变量里，确保 `adb` 命令可以被识别到。
- 同 `Android` + MacOS 测试连接

**关于Win+Android的adb调试添加路径等问题，可以尝试使用Tools文件夹中adb文件夹进行调试，详见adb中readme文件**

## 依赖安装

``` bash
    pip install -r requirements.txt
```

## 原理说明

1. 将手机点击到《跳一跳》小程序界面；
2. 用 ADB 工具获取当前手机截图，并用 ADB 将截图 pull 上来

```shell
    adb shell screencap -p /sdcard/autojump.png
    adb pull /sdcard/autojump.png .
```

3. 计算按压时间
  * 手动版：用 Matplotlib 显示截图，用鼠标点击起始点和目标位置，计算像素距离；
  * 自动版：靠棋子的颜色来识别棋子，靠底色和方块的色差来识别棋盘；

4. 用 ADB 工具点击屏幕蓄力一跳；

```shell
    adb shell input swipe x y x y time(ms)
```


## 安卓手机操作步骤

- 安卓手机打开 USB 调试，设置》开发者选项》USB 调试
- 电脑与手机 USB 线连接，确保执行`adb devices`可以找到设备 ID
- 界面转至微信跳一跳游戏，点击开始游戏
- 运行`python wechat_jump_auto.py`，如果手机界面显示 USB 授权，请点击确认
- 请按照你的手机分辨率从`./config/`文件夹找到相应的配置，拷贝到 *.py 同级目录`./config.json`（如果屏幕分辨率能成功探测，会直接调用 config 目录的配置，不需要复制）


## iOS 手机操作步骤

1. 运行安装好的 `WebDriverAgentRunner`
2. 将手机点击到《跳一跳》小程序界面
3. 运行脚本。有两种模式可供选择：手动辅助跳 和 自动连续跳
    * 手动辅助跳
        * 命令行运行`python3 wechat_jump_iOS_py3.py`
        * 依次点击弹出的窗口中的起始位置和目标位置，会自动计算距离后起跳
        * 根据起跳的精准情况更改`python3 wechat_jump_iOS_py3.py`中的`time_coefficient`参数，直到获得最佳取值
    * 自动连续跳
        * 拷贝`./config/iPhone`目录下对应的设备配置文件，重命名并替换到`./config.json`
        * 命令行运行`python3 wechat_jump_auto_iOS.py`
        * 会自动计算坐标并连续起跳，根据起跳的精准情况更改`./config.json` 中的`press_coefficient`参数，直到获得最佳取值

## 实验结果

![](https://ws1.sinaimg.cn/large/c3a916a7gy1fmxel5dkxvj20u01hcmzx.jpg)

## TODO

- [x] 可以对拉上来的图片进行颜色分割，识别小人和目标中心，这样就不需要手动点击自动弹跳。

> 事实证明，机器人比人更会玩儿游戏。

