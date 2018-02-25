import wda

import settings


class Connector:


    def __init__(self, image_dir=settings.IMAGE_DIR):
        self.image_dir = image_dir

        self.client = wda.Client()
        self.session = self.client.session()


    def connector_screenshot(self):
        self.client.screenshot(self.image_dir)


    def connector_taphold(self, value):
        self.session.tap_hold(200, 200, value)
