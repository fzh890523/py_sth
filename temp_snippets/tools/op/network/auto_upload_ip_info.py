# encoding: utf-8
import datetime
import json
import os
import sys
import optparse

import crypto


sys.modules["Crypto"] = crypto
import paramiko
import netifaces

__author__ = 'fzh89'

g_action = None


def get_home_dir_path() -> str:
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


def get_ip_info():
    ip_infos = {}
    for ifaceName in netifaces.interfaces():
        addresses = [i['addr'] for i in netifaces.ifaddresses(ifaceName).setdefault(
            netifaces.AF_INET, [{'addr': None}])]
        ip_infos[ifaceName] = addresses
    return ip_infos


def prepare_client() -> paramiko.SSHClient:
    host = "yonka-linode-vps-1"  # bobo-aliyun-xueshengji
    username = "raspberry"
    home_dir_path = get_home_dir_path()
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


def upload():
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


def main(a):
    globals()[a]()


if __name__ == "__main__":
    g_help_info = """
    usage:
    python auto_upload_ip_info.py --action=upload
    or
    python auto_upload_ip_info.py --action=get
    \n
    """
    g_parser = optparse.OptionParser(g_help_info)
    g_parser.add_option(
        "-a",
        "--action",
        dest="a",
        help="the action todo, upload ot get",
        default="get",
        action="store"
    )
    g_options, g_args = g_parser.parse_args()
    g_action = g_options.a
    main(g_action)
