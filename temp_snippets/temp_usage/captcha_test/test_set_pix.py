# encoding: utf-8

from PIL import Image
import os
from captcha.image import PixelCurveDrawer

__author__ = 'yonka'

BASE_DIR = "C:\\Users\\bili\\Downloads\\captcha"


single_color_map = {
    0: 128,
    1: 60,
    2: 30,
    3: 10,
    4: 5
}


if __name__ == "__main__":
    im = Image.new('RGBA', (100, 50), (255, 255, 255, 0))
    dr = PixelCurveDrawer()
    dr.do_draw(im, (5, 20), 50, init_angle=-1)
    im.save(os.path.join(BASE_DIR, "test", "t3.png"))
