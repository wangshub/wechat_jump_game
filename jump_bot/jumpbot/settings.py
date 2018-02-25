# Wechat Jump Bot (iOS)
# ----------------------------------------------------------------------------

import os

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
PROJECT_DIR = "jumpbot/"

# ----------------------------------------------------------------------------
# Screenshot

DATA_DIR = "data/"
IMAGE = "screen.png"
IMAGE_DIR = PROJECT_DIR + DATA_DIR + IMAGE

# ----------------------------------------------------------------------------

# mode: ['auto', 'manual']
MODE = "manual"

# ----------------------------------------------------------------------------
# Params

def get_bot_params(model="ip"):

    bot_params = {
        "TIME_COEFF": 2.,
        "COORD_Y_START_SCAN": 200,
        "PIECE_BASE_HEIGHT_HALF": 13,
        "PIECE_BODY_WIDTH": 49,
        "SWIPE_X1": 375,
        "SWIPE_Y1": 1055,
        "SWIPE_X2": 375,
        "SWIPE_Y2": 1055
    }

    if model == "ip":
        bot_params["TIME_COEFF"] = 2.
        bot_params["COORD_Y_START_SCAN"] = 200
        bot_params["PIECE_BASE_HEIGHT_HALF"] = 13
        bot_params["PIECE_BODY_WIDTH"] = 49
        bot_params["SWIPE_X1"] = 375
        bot_params["SWIPE_Y1"] = 1055
        bot_params["SWIPE_X2"] = 375
        bot_params["SWIPE_Y2"] = 1055

    elif model == "plus":
        bot_params["TIME_COEFF"] = 1.2
        bot_params["COORD_Y_START_SCAN"] = 300
        bot_params["PIECE_BASE_HEIGHT_HALF"] = 20
        bot_params["PIECE_BODY_WIDTH"] = 70
        bot_params["SWIPE_X1"] = 320
        bot_params["SWIPE_Y1"] = 410
        bot_params["SWIPE_X2"] = 320
        bot_params["SWIPE_Y2"] = 410

    elif model == "ipx":
        bot_params["TIME_COEFF"] = 1.31
        bot_params["COORD_Y_START_SCAN"] = 170
        bot_params["PIECE_BASE_HEIGHT_HALF"] = 23
        bot_params["PIECE_BODY_WIDTH"] = 70
        bot_params["SWIPE_X1"] = 320
        bot_params["SWIPE_Y1"] = 410
        bot_params["SWIPE_X2"] = 320
        bot_params["SWIPE_Y2"] = 410

    elif model == "se":
        bot_params["TIME_COEFF"] = 2.3
        bot_params["COORD_Y_START_SCAN"] = 190
        bot_params["PIECE_BASE_HEIGHT_HALF"] = 12
        bot_params["PIECE_BODY_WIDTH"] = 50
        bot_params["SWIPE_X1"] = 375
        bot_params["SWIPE_Y1"] = 1055
        bot_params["SWIPE_X2"] = 375
        bot_params["SWIPE_Y2"] = 1055

    else:
        print("ParamError: Unknown model type, model should be [ip, plus, ipx, se]")

    return bot_params
