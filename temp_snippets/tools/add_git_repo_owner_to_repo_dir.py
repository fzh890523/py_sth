# encoding: utf-8

"""
not complete
"""

import os
import glob
import sys
import subprocess
from utils.os import path_util

__author__ = 'yonka'


def get_git_repo_owner(p=None):
    def get_repo_owner():
        try:
            subprocess.check_output("git remote show origin | grep 'Fetch URL:' | awk - F \"/\" '{print $(NF-1)}'")
        except subprocess.CalledProcessError:
            return "", False

    if p is None:
        return get_repo_owner()
    cur_dir = os.getcwd()
    os.chdir(p)
    res = get_repo_owner()
    os.chdir(cur_dir)
    return res


def is_git_dir(p):
    return os.path.exists(os.path.join(p, ".git"))


def _add_user_prefix_to_git_repo_dir(p):
    p = os.path.abspath(p)
    dir_name = os.path.basename(p)
    if "__" in dir_name:
        return
    parent_dir_path = path_util.parent_dir(p)
    if not is_git_dir(p):
        return
    if p == parent_dir_path:
        sys.stderr.write("skip path %s as its parent dir is itself" % p)
        return
    owner, ok = get_git_repo_owner(p)
    if not ok:
        sys.stderr.write("fail for path: %s" % p)
        return
    os.rename(p, os.path.join(parent_dir_path, "%s__%s" % (owner, dir_name)))


def add_user_prefix_to_git_repo_dir(glob_path):
    if os.path.exists(glob_path):
        # 不考虑存在 ./* 这个文件/目录的情况
        _add_user_prefix_to_git_repo_dir(glob_path)
        return
    paths = glob.glob(glob_path)
    path_num = len(paths)
    if path_num == 0:
        print "find no path for give glob_path " + glob_path
        return
    for p in paths:
        _add_user_prefix_to_git_repo_dir(p)