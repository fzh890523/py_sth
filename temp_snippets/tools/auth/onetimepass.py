# encoding: utf-8

import hmac, base64, struct, hashlib
import time
from optparse import OptionParser

__author__ = 'yonka'


def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = ord(h[19]) & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return h


def get_totp_token(secret):
    return get_hotp_token(secret, intervals_no=int(time.time())//30)


def main():
    help_info = """
    usage: -s/--secret
    get code from stdout
    \n
    """
    parser = OptionParser(help_info)

    parser.add_option(
        "-s",
        "--secret",
        dest="s",
        help="the secret",
        action="store"
    )

    options, args = parser.parse_args()
    s = options.s
    print get_totp_token(s)


if __name__ == "__main__":
    main()
