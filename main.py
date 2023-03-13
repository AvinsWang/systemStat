import os
import sys
import logging
import argparse
import traceback
try:
    from itime import iTime
except ModuleNotFoundError:
    raise ModuleNotFoundError("iTime not found, please install py-itime")

import utils
import sysstat
from server import ServerSocket
from client import ClientSocket
import server_config, client_config


server_log = logging.getLogger(server_config.server_log_name)
client_log = logging.getLogger(client_config.client_log_name)


def get_args():
    parser = argparse.ArgumentParser(description='Stat cpu & gpu')
    parser.add_argument('--server', action='store_true', help="Launch server")
    parser.add_argument('--alarm', action='store_true')

    parser.add_argument('--tb_server', action='store_true', help="Launch tensorboard server")
    parser.add_argument('--tb_port', default=6006, help="Tensorboard port")
    parser.add_argument('--bg', action='store_true', help="Launch tensorboard server background")

    parser.add_argument('--local', action='store_true', help="Show system statics on stdout")

    parser.add_argument('--client', action='store_true', help="Launch client")
    parser.add_argument('--client_name', type=str, default='', help="Name to identify different client")
    parser.add_argument('--host', type=str, help="Server host")
    parser.add_argument('--port', type=int, help="Server port")
    parser.add_argument('--plaintext', type=str, default='')
    parser.add_argument('--tz', type=int, default=0, help='Time zone')

    args = parser.parse_args()
    return args


def run():
    args = get_args()
    datetime = iTime.now().datetime_str()
    if args.server:
        os.makedirs(server_config.stat_log_dir, exist_ok=True)
        os.makedirs(server_config.tb_log_dir, exist_ok=True)
        Server = ServerSocket(server_config.server_host, server_config.server_port, server_config.server_cyphertext)
        Server.listening()

    if args.alarm:
        # send alarm to admin
        # use email etc.
        pass

    if args.tb_server:
        cmd = f"python -m tensorboard.main " \
              f"--logdir={server_config.tb_log_dir} " \
              f"--port={args.tb_port} "\
              f"--window_title=systemStatTB " \
              f"--reload_multifile=true " \
              f"--reload_multifile_inactive_secs=60 " \
              f"--bind_all "
        if args.bg:
            cmd += '&'
        os.system(cmd)
        print(f"{datetime}| Tensorboard server launched successfully!")
        print(f"{datetime}| {cmd}")

    if args.local:
        stat_dic = sysstat.sysstat()
        stat_dic.update({'datetime': iTime(stat_dic['datetime']).delta(hours=args.tz).datetime_str()})
        for key, val in stat_dic.items():
            print(key, ":", val)

    if args.client:
        if args.host is None:
            args.host = client_config.server_host
        if args.port is None:
            args.port = client_config.server_port
        if args.client_name == '':
            args.client_name = client_config.client_name
        try:
            stat_dic = sysstat.sysstat()
            stat_dic.update({'datetime': iTime(stat_dic['datetime']).delta(hours=args.tz).datetime_str()})
            stat_dic.update({'client_name': args.client_name})
            Clinet = ClientSocket(args.host, args.port)
            Clinet.init_client()
            state_dic = Clinet.send_msg(stat_dic, plaintext=args.plaintext)
            utils.check_server_return_state(state_dic)
            Clinet.close_client()
        except Exception:
            client_log.info(f"{datetime}| Send system statics to server failed!")
            traceback.print_exc()


if __name__ == '__main__':
    run()
