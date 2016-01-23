# encoding: utf-8

from optparse import make_option

__author__ = 'yonka'

make_option(
    "-f",
    "--file",
    action="store",
    dest="file_path",
    default=".",
    help="file path"
)

if __name__ == "__main__":
    print file_path