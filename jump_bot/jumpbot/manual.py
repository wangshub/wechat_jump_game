import time
import math

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import settings
from connector import Connector
from algos import get_press_time


class ManualBot(Connector):

    def __init__(self, params=settings.get_bot_params()):
        # init connector
        super(ManualBot, self).__init__()

        # init figure
        self.figure = plt.figure()

        # actions
        self.steps = 0
        self.params = params
        self.coords = []
        self.ix = [0, 0]
        self.iy = [0, 0]
        self.click_counter = 0
        self.status = True


    def run(self):
        self.connector_screenshot()
        self.image = plt.imshow(self._read_image(), animated=True)
        self.action()

    def action(self):
        self.figure.canvas.mpl_connect('button_press_event', self._onclick)
        ani = animation.FuncAnimation(self.figure, self._update_figure, interval=50, blit=True)
        plt.show()


    def _onclick(self, event):
        coord = []
        self.ix, self.iy = event.xdata, event.ydata
        coord.append((self.ix, self.iy))
        print("coordinate = ", coord)
        self.coords.append(coord)
        self.click_counter += 1

        if self.click_counter > 1:
            self.click_counter = 0
            # next screen
            coord1 = self.coords.pop()
            coord2 = self.coords.pop()
            press_time = get_press_time(coord1[0][0], coord1[0][1],
                                        coord2[0][0], coord2[0][1], 
                                        self.params["TIME_COEFF"])
            self.steps += 1
            print("Step: ", self.steps)
            print("- coord1: ", coord1)
            print("- coord2: ", coord2)
            print("- press_time: ", press_time)
            self.connector_taphold(press_time)
            self.status = True


    def _update_figure(self, *args):
        if self.status:
            time.sleep(1)
            self.connector_screenshot()
            self.image.set_array(self._read_image())
            self.status = False
        return self.image,


    def _read_image(self):
        return np.array(Image.open(self.image_dir))
