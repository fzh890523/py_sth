# encoding: utf-8
"""
usage: add following line to /etc/rc.local before line "exit 0"
(cd /data/daemons/auto_upload_ip_info && sudo -u yonka nohup python3 auto_upload_ip_info.py --action=monitor >/data/logs/upload_ip_info.log 2>&1 &)
should ensure that script file path and log file path are corrent and have right permission
"""
import datetime
import json
import os
import sys
import optparse
from os.path import expanduser
import time
import logging

if os.name == "nt":
    import crypto

    sys.modules["Crypto"] = crypto
import paramiko
import netifaces

__author__ = 'fzh89'

g_action = None
g_last_ip_info = None


def get_home_dir_path() -> str:
    """
    ~形式的不能在代码里cd，要展开
    """

    def _win_home() -> str:
        home_drive = os.environ.get("HOMEDRIVE")
        home_path = os.environ.get("HOMEPATH")
        if home_drive and home_path:
            return os.path.join(home_drive, home_path)

    oss_home_dir_path = {
        "nt": _win_home,
        "posix": lambda: "~"
    }
    os_name = os.name
    os_home_dir_path_getter = oss_home_dir_path.get(os_name)
    if os_home_dir_path_getter is None:
        return None
    return os_home_dir_path_getter()


def get_ip_info() -> dict:
    ip_infos = {}
    for ifaceName in netifaces.interfaces():
        addresses = [i['addr'] for i in netifaces.ifaddresses(ifaceName).setdefault(
            netifaces.AF_INET, [{'addr': None}])]
        ip_infos[ifaceName] = addresses
    return ip_infos


def prepare_client() -> paramiko.SSHClient:
    host = "yonka-linode-vps-1"  # bobo-aliyun-xueshengji
    username = "raspberry"
    home_dir_path = expanduser("~")
    if not home_dir_path:
        raise SystemError("can not get home dir path")
    private_key_file = os.path.join(home_dir_path, ".ssh", "id_rsa")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        host, username=username,
        key_filename=private_key_file
    )
    return ssh


def may_online(ip_info) -> bool:
    if ip_info is None:
        return False
    for ifname, ifaddr in ip_info.items():
        if not ifaddr:
            continue
        for addr in ifaddr:
            if not addr:
                continue
            # if not ipaddress.ip_address(addr).is_private:
            if not addr.startswith("127"):
                return True
    return False


def upload(ip_info: dict=None):
    if ip_info is None:
        ip_info = get_ip_info()
    info_to_send = {
        "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "ip_info": ip_info
    }
    info_str = json.dumps(info_to_send)

    ssh = prepare_client()
    cmd_stdin, cmd_stdout, cmd_stderr = ssh.exec_command("cat > ~/cur_ip_info.txt")
    cmd_stdin.write(info_str)
    cmd_stdin.write("\n")
    cmd_stdin.close()
    # print(cmd_stderr.read())
    # print(cmd_stdout.read())
    ssh.close()


def get():
    ssh = prepare_client()
    cmd_stdin, cmd_stdout, cmd_stderr = ssh.exec_command("cat  ~/cur_ip_info.txt")
    print(cmd_stdout.read())
    ssh.close()


def cmp_addr_info(last_one, new_one):
    if last_one is None:
        if new_one is None:
            return True
        else:
            return False
    if new_one is None:
        return False
    if len(last_one) != len(new_one):
        return False
    for last_addr, new_addr in zip(last_one, new_one):
        if last_addr != new_addr:
            return False
    return True


def cmp_ip_info(last_one, new_one):
    if last_one is None:
        if new_one is not None:
            return False
    if new_one is None:
        return True
    if len(last_one) != len(new_one):
        return False
    for ifname, ifaddr in last_one.items():
        if not cmp_addr_info(ifaddr, new_one.get(ifname)):
            return False
    return True


def monitor(intervals=5):
    global g_last_ip_info
    while True:
        time.sleep(intervals)
        ip_info = get_ip_info()
        if ip_info is not None and not cmp_ip_info(g_last_ip_info, ip_info) and may_online(ip_info):
            logging.info("last_info is %s, new_info is %s, do upload", g_last_ip_info, ip_info)
            upload(ip_info)
            g_last_ip_info = ip_info


def main(a):
    globals()[a]()


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    g_help_info = """
    usage:
    python auto_upload_ip_info.py --action=upload
    or
    python auto_upload_ip_info.py --action=get
    or
    python auto_upload_ip_info.py --action=monitor
    \n
    """
    g_parser = optparse.OptionParser(g_help_info)
    g_parser.add_option(
        "-a",
        "--action",
        dest="a",
        help="the action todo, upload ot get or monitors",
        default="get",
        action="store"
    )
    g_options, g_args = g_parser.parse_args()
    g_action = g_options.a
    main(g_action)
