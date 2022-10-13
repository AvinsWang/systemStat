import os
import sys
import argparse
import traceback
from itime import iTime

import config
import utils
import sysstat
from server import ServerSocket
from client import ClientSocket


def get_args():
    parser = argparse.ArgumentParser(description='Stat cpu & gpu')
    parser.add_argument('--server', action='store_true', help="Launch server")
    parser.add_argument('--client', action='store_true', help="Launch client")
    parser.add_argument('--tz', type=int, default=0, help='Time zone')
    parser.add_argument('--plaintext', type=str, default='')
    parser.add_argument('--local', action='store_true', help="Show system static on stdout")
    parser.add_argument('--host', type=str, help="Server host")
    parser.add_argument('--port', type=int, help="Server port")
    parser.add_argument('--tb_server', action='store_true', help="Launch tensorboard server")
    parser.add_argument('--bg', action='store_true', help="Launch tensorboard server background")
    parser.add_argument('--alarm', action='store_true')
    args = parser.parse_args()
    return args


def run():
    args = get_args()
    datetime = iTime.now().datetime_str()
    if args.server:
        Server = ServerSocket(config.server_host, config.server_port, config.server_cyphertext)
        Server.listening()
    if args.client:
        if args.host is None:
            args.host = config.server_host
        if args.port is None:
            args.port = config.server_port
        try:
            stat_dic = sysstat.sysstat()
            stat_dic.update({'datetime': iTime(stat_dic['datetime']).delta(hours=args.tz).datetime_str()})
            Clinet = ClientSocket(args.host, args.port)
            Clinet.init_client()
            state_dic = Clinet.send_msg(stat_dic, plaintext=args.plaintext)
            utils.check_server_return_state(state_dic)
            Clinet.close_client()
        except Exception:
            print(f"{datetime}| Send system statics to server failed!")
            traceback.print_exc()
    if args.local:
        stat_dic = sysstat.sysstat()
        stat_dic.update({'datetime': iTime(stat_dic['datetime']).delta(hours=args.tz).datetime_str()})
        for key, val in stat_dic.items():
            print(key, ":", val)
    if args.tb_server:
        cmd = f"python -m tensorboard.main " \
              f"--logdir={config.tb_log_dir} " \
              f"--window_title=systemStatTBz " \
              f"--reload_multifile=true " \
              f"--reload_multifile_inactive_secs=60 " \
              f"--bind_all "
        if args.bg:
            cmd += '&'
        os.system(cmd)
        print(f"{datetime}| Tensorboard server launched successfully!")
        print(f"{datetime}| {cmd}")


if __name__ == '__main__':
    run()
