# encoding: utf-8

import os
import sys
import glob
from optparse import OptionParser

__author__ = 'yonka'


def contain_non_ok_file(p):
    pps = os.listdir(p)
    for pp in pps:
        name = os.path.basename(pp)
        if os.path.isfile(pp) and is_not_ok(name):
            return True
    return False


def is_not_ok(filename):
    # return filename.endswith(".td")  # xunlei version
    return ".baiduyun." in filename  # baiduyun version


def sep_dir_and_file(dir_p, ps):
    dirs, files = [], []
    for p in ps:
        p = os.path.join(dir_p, p)
        if os.path.isdir(p):
            dirs.append(p)
        elif os.path.isfile(p):
            files.append(p)
        else:
            sys.stderr.write("path %s is neither dir nor file" % p)
    return dirs, files


# should be both
def _begin_sync(src, dst):
    to_sync_dirs = [src]
    while to_sync_dirs:
        cur_dir = to_sync_dirs.pop()
        dst_path = os.path.realpath(os.path.join(dst, os.path.relpath(cur_dir, src)))
        print "sync dir %s to %s" % (cur_dir, dst_path)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        try:
            dirs, files = sep_dir_and_file(cur_dir, os.listdir(cur_dir))
            to_sync_dirs.extend(dirs)
            for f in files:
                if not is_not_ok(f):
                    dst_file_path = os.path.join(dst_path, os.path.basename(f))
                    if os.path.exists(dst_file_path):
                        sys.stderr.write("ignore path %s as dst_path %s has existed" % (f, dst_file_path))
                        continue
                    print "\tsync file %s to %s" % (f, dst_file_path)
                    os.rename(f, dst_file_path)
                else:
                    print "skip unfinished file %s" % f
        except Exception as e:
            sys.stderr.write("ERROR: met exception %s when process path %s, skip" % (e, cur_dir))


def mv_dir(src, dst_base):
    """
    允许 /a/b/c ---> /a1/b1，此时会在b1下创建c；
    也允许 /a/b/c ---> /a1/b1/c，此时会...
    """
    src = [os.path.abspath(src_item) for src_item in glob.glob(src)]
    if len(src) != 1:
        for src_item in src:
            mv_dir(src_item, dst_base)
    else:
        src = src[0]
        dst_base = os.path.abspath(dst_base)
        src_name = os.path.basename(src)
        dst_base_name = os.path.basename(dst_base)
        if dst_base_name == src_name:
            dst = dst_base
        else:
            dst = os.path.join(dst_base, src_name)
        if not os.path.exists(dst):
            os.makedirs(dst)
        _begin_sync(src, dst)

if __name__ == "__main__":
    """
    example: python C:\Users\bili\PycharmProjects\yonka_test\python ipy\mv_ok_dir.py --src=H:\BaiduYunDownload\古典SACD  --dst=K:\media\古典SACD
    """
    parser = OptionParser("python %s --src=${src_path} --dst=${dst_path}" % (
        os.path.basename(__file__),))
    parser.add_option(
        "-s",
        "--src",
        dest="src",
        help="the src dir path to sync",
        action="store"
    )
    parser.add_option(
        "-d",
        "--dst",
        dest="dst",
        help="the dst dir path to sync to",
        action="store",
    )
    options, args = parser.parse_args()
    src, dst = options.src, options.dst
    mv_dir(src, dst)
