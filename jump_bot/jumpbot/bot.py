import argparse

import settings
from auto import AutoBot
from manual import ManualBot


def config():
    parser = argparse.ArgumentParser(description='Wechat Jump Bot')
    parser.add_argument('-ml', '--model', 
                        type=str,
                        help='device model = [ip, plus, ipx, se]',
                        required=True)

    parser.add_argument('-me', '--mode', 
                        type=str,
                        help='mode = [auto, manual]',
                        required=True)

    return parser.parse_args()


def jumpbot(parser):
 
    if parser.mode == "manual":
        bot = ManualBot(params=settings.get_bot_params(parser.model))
        bot.run()

    elif parser.mode == "auto":
        bot = AutoBot(params=settings.get_bot_params(parser.model)) 
        bot.run()

    else:
        print("ParamError: MODE should be ['auto', 'manual'].")


if __name__ == '__main__':

    parser = config()
    jumpbot(parser)    
