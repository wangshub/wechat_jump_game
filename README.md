# 教你用 Python 來玩微信跳一跳
[![GitHub stars](https://img.shields.io/github/stars/wangshub/wechat_jump_game.svg)](https://github.com/wangshub/wechat_jump_game/stargazers) [![GitHub forks]( https://img.shields.io/github/forks/wangshub/wechat_jump_game.svg)](https://github.com/wangshub/wechat_jump_game/network) [![GitHub license](https://img.shields .io/github/license/wangshub/wechat_jump_game.svg)](https://github.com/wangshub/wechat_jump_game/blob/master/LICENSE)

[![Throughput Graph](https://graphs.waffle.io/wangshub/wechat_jump_game/throughput.svg)](https://waffle.io/wangshub/wechat_jump_game/metrics/throughput)

## 遊戲模式

> 2017 年 12 月 28 日下午，微信發布了 6.6.1 版本，加入了「小遊戲」功能，並提供了官方 DEMO「跳一跳」。這是一個 2.5D 插畫風格的益智遊戲，玩家可以通過按壓屏幕時間的長短來控制這個「小人」跳躍的距離。分數越高，那麼在好友排行榜更加靠前。通過 Python 腳本自動運行，讓你輕鬆霸榜。

![](./resource/image/jump.gif)

可能剛開始上手的時候，因為時間距離之間的關係把握不恰當，只能跳出幾個就掉到了台子下面。 **如果能利用圖像識別精確測量出起始和目標點之間測距離，就可以估計按壓的時間來精確跳躍。 **

## 原理說明

##### 由於微信檢測非常嚴厲，這裡的防禁代碼可能已經不起作用，主要供學習用途

1. 將手機點擊到《跳一跳》小程序界面

2. 用 ADB 工具獲取當前手機截圖，並用 ADB 將截圖 pull 上來
```shell
adb shell screencap -p /sdcard/autojump.png
adb pull /sdcard/autojump.png .
```

3. 計算按壓時間
  * 手動版：用 Matplotlib 顯示截圖，用鼠標先點擊起始點位置，然後點擊目標位置，計算像素距離；
  * 自動版：靠棋子的顏色來識別棋子，靠底色和方塊的色差來識別棋盤；

4. 用 ADB 工具點擊屏幕蓄力一跳
```shell
adb shell input swipe x y x y time(ms)
```



## 使用教程

相關軟件工具安裝和使用步驟請參考[Android 和iOS 操作步驟](https://github.com/wangshub/wechat_jump_game/wiki/Android-%E5%92%8C-iOS-%E6%93%8D%E4 %BD%9C%E6%AD%A5%E9%AA%A4)

#### 獲取源碼

```
- git clone https://github.com/wangshub/wechat_jump_game.git

```
##### 非常推薦使用Python3，避免編碼及import問題
## PR 要求
##### 請選擇 merge 進 master 分支，並且標題寫上簡短描述，例子
[優化] 使用PEP8優化代碼

## 版本說明

- master 分支：穩定版本，已通過測試
- dev 分支：開發版本，包含一些較穩定的新功能，累計多個功能並測試通過後合併至 prod 分支
- 其他分支：功能開發 (feature) 或問題修復 (bugfix)，屬於最新嚐鮮版本，可能處於開發中的狀態，基本完成後合併至 dev 分支

## FAQ

- 詳見 [Wiki-FAQ](https://github.com/wangshub/wechat_jump_game/wiki/FAQ)

## 更新日誌

- 詳見 [changelog](https://github.com/wangshub/wechat_jump_game/blob/master/changelog.md)

## 開發者列表

- 詳見 [contributors](https://github.com/wangshub/wechat_jump_game/graphs/contributors)

## 交流

- 314659953 (1000 人)
- 176740763 (500 人)

- 或者關注我的微信公眾號後台留言

![](./resource/image/qrcode_for_gh_3586401957c4_258.jpg)