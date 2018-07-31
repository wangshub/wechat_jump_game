##############################################################################
Wechat Jump Bot (iOS)
##############################################################################

==============================================================================
Features
==============================================================================

- Auto Mode: play the game automatically;
- Manual Mode: play the game manually.

Wechat Jump Game

.. image:: https://github.com/alpesis-ai/wechat-jumpbot/blob/master/images/auto.png
   :height: 1334px
   :width: 500px


==============================================================================
How it runs
==============================================================================

Prerequisites

- WebDriverAgent
- libimobiledevice
- Python 3

WebDriverAgent

::

    $ git clone https://github.com/facebook/WebDriverAgent && cd WebDriverAgent
    $ brew install carthage
    $ ./Scripts/bootstrap.sh
    # open WebDriverAgent.xcodeproj with Xcode
    # Xcode:
    # - code sign (general and build_settings): WebDriverAgentLib/WebDriverAgentRunner
    # - Product -> Destination -> <your device>
    # - Product -> Scheme -> WebDriverAgentRunner
    # - Product -> Test

libimobiledevice (iproxy)

::

    $ brew install libimobiledevice
    $ iproxy 8100 8100
    # browse: http://localhost:8100/status
    # browse: http://localhost:8100/inspector

Bot Agent (iOS)

::

    $ git clone https://github.com/alpesis-ai/wechat-jumpbot.git
    $ cd bot-agent-ios

    $ pip3 install --pre facebook-wda
    $ pip3 install -r requirements.txt

    # make run
    # - model: [ip, plus, ipx, se]
    # - mode: [auto, manual]
    # python3 jumpbot/bot.py --model <device_model> --mode <mode>
    $ mkdir -p jumpbot/data
    # iphone 6/7
    $ python3 jumpbot/bot.py --model ip --mode auto
    # iphone 6/7 plus
    $ python3 jumpbot/bot.py --model plus --mode auto
    # iphone X
    $ python3 jumpbot/bot.py --model ipx --mode auto
    # iphone SE
    $ python3 jumpbot/bot.py --model se --mode auto


==============================================================================
Algorithms
==============================================================================

Manual Mode:

- click the piece(x, y) and board(x, y) and get the coordinates correspondingly
- calculating the distance and press time

::

    (coord1[0][0] - coord2[0][0])**2 + (coord2[0][1] - coord2[0][1])**2
    distance = distance ** 0.5
    press_time = distance * settings.TIME_COEFF

Auto Mode:

- the main idea same as the manual mode, but detecting the piece and the board automatically
    - find coord_y_start_scan
    - find piece
    - find board


==============================================================================
Developement
==============================================================================

::

    connector ---| 
                 | --> auto / manual  --> bot
    algos     ---|
