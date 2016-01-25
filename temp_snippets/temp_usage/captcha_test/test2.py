# encoding: utf-8
"""
requirements_start
git url=https://bitbucket.org/fzh890523/bb_captcha;name=captcha;commit=1e5e0a5385c8b8109da4a6df0cbac96b0ac4f5c3;\
branch=master
requirements_end
"""

from threading import Thread
import os
import itertools
import random
import sys
import shutil
import ConfigParser
from optparse import OptionParser

__author__ = 'yonka'

must_text = "12ab"
fmt_suffix = {
    "jpeg": "jpg"
}


def do_image():
    # image = ImageCaptcha(fonts=['./comic.ttf', './comicbd.ttf'])
    image = ImageCaptcha(width=100, height=50)

    # data = image.generate('1234')
    # assert isinstance(data, BytesIO)
    image.write('1234', 'out.%s' % fmt_suffix.get(fmt, fmt), fmt=fmt)


def do_stress_image():
    ts = []
    ss = []
    for i in itertools.chain(
            xrange(ord("a"), ord("z") + 1),
            xrange(ord("A"), ord("Z") + 1),
            xrange(ord("0"), ord("9") + 1)):
        ss.append(chr(i))
    texts = set()
    while len(texts) < 100:
        new_t = "".join(random.sample(ss, 4))
        if new_t in texts:
            continue
        texts.add(new_t)
    if must_text not in texts:
        texts.pop()
        texts.add(must_text)

    def stress_image(i):
        image = ImageCaptcha(width=100, height=50, fonts=['./Mirvoshar.ttf'], font_sizes=[50, 54, 57, 64])
        d = str(i)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        for t in texts:
            image.write(t, os.path.join(d, '%s.%s' % (t, fmt_suffix.get(fmt, fmt))), fmt=fmt)

    for i in range(1):
        t = Thread(target=stress_image, args=(i,))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()


def main():
    # do_image()
    # do_audio()
    if action == "batch":
        do_stress_image()
    elif action == "single":
        do_image()
    else:
        sys.stderr.write("wrong action %s\n" % action)
        sys.exit(1)


if __name__ == "__main__":
    help_info = """
    usage:
    python test2.py png --path E:\\yonka\\git\\yonka\\bili\\bb_captcha
    \n
    """
    parser = OptionParser(help_info)

    parser.add_option(
        "--path",
        dest="path",
        help="the additional python path",
        default="",
        action="store"
    )    
    parser.add_option(
        "--fmt",
        dest="fmt",
        help="the pic fmt",
        default="jpeg",
        action="store"
    )        
    parser.add_option(
        "--action",
        dest="action",
        help="action to do",
        default="batch",
        action="store"
    )            
    options, args = parser.parse_args()
    path, fmt, action = options.path, options.fmt, options.action
    if path:
        paths = [os.path.abspath(p) for p in path.split(";") if p]
        for p in paths:
            if p not in sys.path:
                sys.path.append(p)
        print paths
    from captcha.image import ImageCaptcha  # notice: use bb_captcha rather ...
    main()
