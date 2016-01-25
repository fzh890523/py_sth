# encoding: utf-8
from io import BytesIO
from captcha.image import ImageCaptcha, WheezyCaptcha
from threading import Thread
import os
import itertools
import random
import sys

__author__ = 'yonka'

must_text = "12ab"


def do_audio():
    audio = AudioCaptcha(voicedir='./')

    data = audio.generate('1234')
    assert isinstance(data, bytearray)
    audio.write('1234', 'out.wav')


def do_image():
    # image = ImageCaptcha(fonts=['./comic.ttf', './comicbd.ttf'])
    image = ImageCaptcha(width=100, height=50)

    # data = image.generate('1234')
    # assert isinstance(data, BytesIO)
    f = sys.argv[1]
    image.write('1234', 'out.%s' % f, fmt=f)


def do_stress_image():
    ts = []
    ss = []
    for i in itertools.chain(xrange(ord("a"), ord("z") + 1), xrange(ord("A"), ord("Z") + 1), xrange(ord("0"), ord("9") + 1)):
        ss.append(chr(i))
    texts = set()
    f = sys.argv[1]
    while len(texts) < 100:
        new_t = "".join(random.sample(ss, 4))
        if new_t in texts:
            continue
        texts.add(new_t)
    if must_text not in texts:
        texts.pop()
        texts.add(must_text)

    def stress_image(i):
        image = ImageCaptcha(width=200, height=100, fonts=['./Mirvoshar.ttf'])
        d = str(i)
        os.makedirs(d)
        for t in texts:
            image.write(t, os.path.join(d, '%s.%s' % (t, f)), fmt=f)

    for i in range(1):
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