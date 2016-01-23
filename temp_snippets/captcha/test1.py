# encoding: utf-8

__author__ = 'yonka'

from matplotlib.font_manager import findSystemFonts
import random
from PIL import ImageFont, Image, ImageDraw
import numpy
from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.pyplot as plt


def rand_font(fonts=[], fontpaths=None, fontext='ttf', font_encoding='', min_size=24, max_size=36):
    if fonts == []:
        fonts = findSystemFonts(fontpaths, fontext)
    requested_font = fonts[random.randint(0, len(fonts)-1)]
    font_size = random.randint(min_size, max_size)
    return ImageFont.truetype(requested_font, font_size, encoding=font_encoding)


def create_captcha(text):
    def _rand_color():
        colors = ['red', 'orange', 'purple', 'green', 'yellow']
        return colors[random.randint(0, len(colors)-1)]

    # First font just gets the general offsets
    font = rand_font()
    text_width, text_height = font.getsize(text)

    # Dont draw text here first
    img = Image.new("L", (text_width * 3, text_height * 3), "white")
    draw = ImageDraw.Draw(img)

    fig = plt.figure(figsize=(12, 8))
    axes = Axes3D(fig)

    # Do this way if you want random fonts AND colors
    #=================
    prev_x = 0
    for character in text:
        cfont = rand_font()
        char_wid, char_height = cfont.getsize(character)
        draw.text((prev_x+text_width, text_height), character, font=cfont)

        X, Y = numpy.meshgrid(range(prev_x+text_width, prev_x+text_width+char_wid),
                              range(text_height, text_height+char_height))
        Z = 1 - numpy.asarray(img.crop((prev_x+text_width, text_height,
                                        prev_x+text_width+char_wid,
                                        text_height+char_height))) / 255
        axes.plot_wireframe(X, -Y, Z, rstride=1, cstride=1, color=_rand_color())

        prev_x += char_wid # trying to offset the characters by an x value so they dont overlap
    #=================

    # Do this way if you want just random fonts on each letter all one color
    #=================
    prev_x = 0
    for character in text:
        cfont = rand_font()
        char_wid, char_height = cfont.getsize(character)
        draw.text((prev_x+text_width, text_height), character, font=cfont)

        prev_x += char_wid # trying to offset the characters by an x value so they dont overlap

    X, Y = numpy.meshgrid(range(img.size[0]), range(img.size[1]))
    Z = 1 - numpy.asarray(img) / 255
    axes.plot_wireframe(X, -Y, Z, rstride=1, cstride=1, color=_rand_color())
    #=================

    axes.set_zlim((-3, 3))
    axes.set_xlim((text_width * 1.1, text_width * 1.9))
    axes.set_ylim((-text_height * 1.9, -text_height* 1.1))
    axes.set_axis_off()
    axes.view_init(elev=60, azim=-90)
    plt.show()

create_captcha('TEST')