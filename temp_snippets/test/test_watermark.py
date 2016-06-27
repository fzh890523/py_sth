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


def get_n_channel_pic(pics, n):
    res = None
    if n == 1:
        res = pics[1] if 1 in pics else cv2.cvtColor(
            pics.get(3) if 3 in pics else pics[4], cv2.COLOR_RGB2GRAY)  # 都没有就gg
    elif n == 3:
        res = pics[3] if 3 in pics is not None else (
            cv2.cvtColor(pics[4], cv2.COLOR_RGBA2RGB) if 4 in pics else cv2.cvtColor(pics[2], cv2.COLOR_GRAY2RGB))
    elif n == 4:
        pics[3] = pics[4] if 4 in pics else (
            cv2.cvtColor(pics[3], cv2.COLOR_RGB2RGBA) if 3 in pics else cv2.cvtColor(pics[2], cv2.COLOR_GRAY2RGBA))
    else:
        raise ValueError("n %s is not valid channel number", n)
    if res is not None:
        pics[n] = res
    return res


def image_channel_num(img):
    return 1 if len(img.shape) == 2 else img.shape[2]  # grey pic(h, w) or rgb pic(h, w, channels)


def do_watermark(args):
    # load the watermark image, making sure we retain the 4th channel
    # which contains the alpha transparency
    # watermark = cv2.imread(args["watermark"], cv2.IMREAD_UNCHANGED)
    watermark = cv2.imread(args["watermark"], -1)
    (w_h, w_w) = watermark.shape[:2]
    wm_channel_num = image_channel_num(watermark)

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
    if args["correct"] > 0 and wm_channel_num == 4:  # only for A channel(transparent) exist case
        wm_channels = cv2.split(watermark)
        for i in range(wm_channel_num - 1):
            wm_channels[i] = cv2.bitwise_and(wm_channels[i], wm_channels[i], mask=wm_channels[wm_channel_num - 1])
        watermark = cv2.merge(wm_channels)

    watermark_pics = {wm_channel_num: watermark}

    # loop over the input images
    if os.path.isfile(args["input"]):
        imgs = [args["input"]]
    else:
        imgs = paths.list_images(args["input"])
    for imagePath in imgs:
        # load the input image, then add an extra dimension to the
        # image (i.e., the alpha transparency)
        cur_img = cv2.imread(imagePath)
        (img_h, img_w) = cur_img.shape[:2]
        cur_img_channel_num = image_channel_num(cur_img)

        if abs_pos_x >= img_w or abs_pos_y >= img_h:
            logging.warn(
                "watermark is out of img, use original img. pos_x is %d, pos_y is %d while img_w is %d and img_h is %d",
                pos_x, pos_y, img_w, img_h)
            output = cur_img
        else:
            print "image is %s" % cur_img
            # cur_img = np.dstack([cur_img, np.ones((img_h, img_w), dtype="uint8") * 255])
            # TODO 比较一下对无alpha通道的pic直接这样addweight效果如何
            cur_pos_x = pos_x if pos_x >= 0 else img_w + pos_x
            cur_pos_y = pos_y if pos_y >= 0 else img_h + pos_y
            cur_watermark = get_n_channel_pic(watermark_pics, cur_img_channel_num)
            if dir_v:
                cur_watermark_w = img_w - cur_pos_x if w_w + cur_pos_x > img_w else w_w
                cur_watermark_h = img_h - cur_pos_y if w_h + cur_pos_y > img_h else w_h
                if cur_watermark_w != w_w or cur_watermark_h != w_h:
                    cur_watermark = cur_watermark[0:cur_watermark_h, 0:cur_watermark_w]
            else:
                cur_watermark_w = w_w - cur_pos_x if cur_pos_x - w_w < 0 else w_w
                cur_watermark_h = w_h - cur_pos_y if cur_pos_y - w_h < 0 else w_h
                if cur_watermark_w != w_w or cur_watermark_h != w_h:
                    cur_watermark = cur_watermark[w_h - cur_watermark_h:w_h, w_w - cur_watermark_w:w_w]

            # construct an overlay that is the same size as the input
            # image, (using an extra dimension for the alpha transparency),
            # then add the watermark to the overlay in the bottom-right
            # corner
            overlay = np.zeros((img_h, img_w, wm_channel_num), dtype="uint8")
            # overlay[img_h - w_h - 10:img_h - 10, img_w - w_w - 10:img_w - 10] = watermark
            print "cur_pos_x %d, cur_pos_y %d\ncur_watermark_w %d, cur_watermark_h %d, cur_watermark is %s" % (
                cur_pos_x, cur_pos_y, cur_watermark_w, cur_watermark_h, cur_watermark
            )
            if dir_v:
                overlay[cur_pos_y:cur_pos_y + cur_watermark_h, cur_pos_x:cur_pos_x + cur_watermark_w] = cur_watermark
            else:
                overlay[cur_pos_y - cur_watermark_h:cur_pos_y, cur_pos_x - cur_watermark_w:cur_pos_x] = cur_watermark

            # blend the two images together using transparent overlays
            output = cur_img.copy()
            print "start!!!"
            print overlay
            print output
            print wm_channel_num
            cv2.addWeighted(overlay, args["alpha"], output, args["beta"], 0, output)

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
    """
    dst[I] = saturate(src1[I] * alpha + src2[I] * beta + gramma)，这里gramma为0然后src1为watermark，src2为原图，beta为1。
    alpha=1, beta=1表示完全原色叠加；alpha=1, beta=0表示完全水印（其他为黑）。
    """
    g_ap.add_argument("-a", "--alpha", type=float, default=0.25,
                      help="alpha transparency of the overlay (smaller is more transparent)")
    g_ap.add_argument("-b", "--beta", type=float, default=1.0,
                      help="alpha transparency of the overlay (smaller is more transparent)")
    g_ap.add_argument("-c", "--correct", type=int, default=1,
                      help="flag used to handle if bug is displayed or not")
    """
    以左上角为基准，正x表示离左边的距离为abs(x)，负x表示离右边的距离为abs(x)；y同理
    默认为 0,0也即为左上角
    """
    g_ap.add_argument(
        "-p", "--pos", default=None,
        help="the pos of left-up-corner or right-down-corner according to dir arg, default None means 0_0. "
             "If contains negative value only -p=-1_-1 or --pos=-1_-1 format is supported")
    """
    默认值0表示：pos为水印右下角（同时尽量保全水印右下角部分，一般是可以的），一般对应负数pos，如 -10_-10
    1表示： pos为水印左上角位置（同时也尽量保全水印左上角部分）；一般对应正数pos，如10_10
    """
    g_ap.add_argument(
        "-d", "--dir", type=int, default=0, help="1 means left-up-corner; (default)0 means right-down-corner")
    g_args = vars(g_ap.parse_args())
    do_watermark(g_args)
