# encoding: utf-8
from io import BytesIO
from captcha.audio import AudioCaptcha
from captcha.image import ImageCaptcha, WheezyCaptcha
from threading import Thread
import os
import itertools
import random
from wheezy.captcha.image import noise

__author__ = 'yonka'


def do_audio():
    audio = AudioCaptcha(voicedir='./')

    data = audio.generate('1234')
    assert isinstance(data, bytearray)
    audio.write('1234', 'out.wav')


def do_image():
    # image = ImageCaptcha(fonts=['./comic.ttf', './comicbd.ttf'])
    image = ImageCaptcha()

    # data = image.generate('1234')
    # assert isinstance(data, BytesIO)
    image.write('1234', 'out.jpeg', format="jpeg")    


def do_stress_image():
    ts = []
    ss = []
    for i in itertools.chain(xrange(ord("a"), ord("z") + 1), xrange(ord("A"), ord("Z") + 1), xrange(ord("0"), ord("9") + 1)):
        ss.append(chr(i))
    texts = set()
    while len(texts) < 1000:
        new_t = "".join(random.sample(ss, 4))
        if new_t in texts:
            continue
        texts.add(new_t)

    def stress_image(i):
        image = WheezyCaptcha()
        d = str(i)
        os.makedirs(d)
        for t in texts:
            image.write(t, os.path.join(d, '%s.jpeg' % t), format="jpeg")

    for i in range(8):
        t = Thread(target=stress_image, args=(i,))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()


def main():
    # do_image()
    # do_audio()
    do_stress_image()


if __name__ == "__main__":
    main()