# encoding: utf-8
# import the necessary packages
import argparse
import os
import logging

import numpy as np
import cv2
from imutils import paths

__author__ = 'yonka'

g_args = None
g_ap = None


def do_watermark(args):
    # load the watermark image, making sure we retain the 4th channel
    # which contains the alpha transparency
    # watermark = cv2.imread(args["watermark"], cv2.IMREAD_UNCHANGED)
    watermark = cv2.imread(args["watermark"], -1)
    (w_h, w_w) = watermark.shape[:2]

    pos_x, pos_y = 0, 0
    dir_v = args["dir"]
    pos_str = args["pos"]
    if pos_str is not None:
        pos_x, pos_y = [int(s) for s in pos_str.split("_")]

    abs_pos_x, abs_pos_y = abs(pos_x), abs(pos_y)

    # split the watermark into its respective Blue, Green, Red, and
    # Alpha channels; then take the bitwise AND between all channels
    # and the Alpha channels to construct the actaul watermark
    # NOTE: I'm not sure why we have to do this, but if we don't,
    # pixels are marked as opaque when they shouldn't be
    if args["correct"] > 0:
        (B, G, R, A) = cv2.split(watermark)
        B = cv2.bitwise_and(B, B, mask=A)
        G = cv2.bitwise_and(G, G, mask=A)
        R = cv2.bitwise_and(R, R, mask=A)
        watermark = cv2.merge([B, G, R, A])

    # loop over the input images
    for imagePath in paths.list_images(args["input"]):
        # load the input image, then add an extra dimension to the
        # image (i.e., the alpha transparency)
        image = cv2.imread(imagePath)
        (img_h, img_w) = image.shape[:2]

        if abs_pos_x >= img_w or abs_pos_y >= img_h:
            logging.warn(
                "watermark is out of img, use original img. pos_x is %d, pos_y is %d while img_w is %d and img_h is %d",
                pos_x, pos_y, img_w, img_h)
            output = image
        else:
            image = np.dstack([image, np.ones((img_h, img_w), dtype="uint8") * 255])
            cur_pos_x = pos_x if pos_x >= 0 else img_w + pos_x
            cur_pos_y = pos_y if pos_y >= 0 else img_h + pos_y
            cur_watermark = watermark
            if dir_v:
                cur_watermark_w = img_w - cur_pos_x if w_w + cur_pos_x > img_w else w_w
                cur_watermark_h = img_h - cur_pos_y if w_h + cur_pos_y > img_h else w_h
                if cur_watermark_w != w_w or cur_watermark_h != w_h:
                    cur_watermark = watermark[0:cur_watermark_h, 0:cur_watermark_w]
            else:
                cur_watermark_w = w_w - cur_pos_x if cur_pos_x - w_w < 0 else w_w
                cur_watermark_h = w_h - cur_pos_y if cur_pos_y - w_h < 0 else w_h
                if cur_watermark_w != w_w or cur_watermark_h != w_h:
                    cur_watermark = watermark[w_h - cur_watermark_h:w_h, w_w - cur_watermark_w:w_w]

            # construct an overlay that is the same size as the input
            # image, (using an extra dimension for the alpha transparency),
            # then add the watermark to the overlay in the bottom-right
            # corner
            overlay = np.zeros((img_h, img_w, 4), dtype="uint8")
            # overlay[img_h - w_h - 10:img_h - 10, img_w - w_w - 10:img_w - 10] = watermark
            print "cur_pos_x %d, cur_pos_y %d\ncur_watermark_w %d, cur_watermark_h %d, cur_watermark is %s" % (
                cur_pos_x, cur_pos_y, cur_watermark_w, cur_watermark_h, cur_watermark
            )
            if dir_v:
                overlay[cur_pos_y:cur_pos_y + cur_watermark_h, cur_pos_x:cur_pos_x + cur_watermark_w] = cur_watermark
            else:
                overlay[cur_pos_y - cur_watermark_h:cur_pos_y, cur_pos_x - cur_watermark_w:cur_pos_x] = cur_watermark

            # blend the two images together using transparent overlays
            output = image.copy()
            cv2.addWeighted(overlay, args["alpha"], output, 1.0, 0, output)

        # write the output image to disk
        filename = imagePath[imagePath.rfind(os.path.sep) + 1:]
        p = os.path.sep.join((args["output"], filename))
        cv2.imwrite(p, output)


if __name__ == "__main__":
    logging.basicConfig(format=u'%(asctime)s %(message)s', datefmt=u'%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    # construct the argument parse and parse the arguments
    g_ap = argparse.ArgumentParser()
    g_ap.add_argument("-w", "--watermark", required=True,
                      help="path to watermark image (assumed to be transparent PNG)")
    g_ap.add_argument("-i", "--input", required=True,
                      help="path to the input directory of images")
    g_ap.add_argument("-o", "--output", required=True,
                      help="path to the output directory")
    g_ap.add_argument("-a", "--alpha", type=float, default=0.25,
                      help="alpha transparency of the overlay (smaller is more transparent)")
    g_ap.add_argument("-c", "--correct", type=int, default=1,
                      help="flag used to handle if bug is displayed or not")
    g_ap.add_argument(
        "-p", "--pos", default=None,
        help="the pos of left-up-corner or right-down-corner according to dir arg, default None means 0_0. "
             "If contains negative value only -p=-1_-1 or --pos=-1_-1 format is supported")
    g_ap.add_argument(
        "-d", "--dir", type=int, default=0, help="1 means left-up-corner; (default)0 means right-down-corner")
    g_args = vars(g_ap.parse_args())
    do_watermark(g_args)
