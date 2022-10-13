import json
import os
import socket
import traceback
import os.path as osp
from itime import iTime

import config
import utils


class ServerSocket:
    def __init__(self, host, port, cyphertext, backlog=5, buf_size=1024):
        self.host = host
        self.port = port
        self.cyphertext = cyphertext
        self.backlog = backlog
        self.buf_size = buf_size
        self._init_server()

    def _init_server(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
            print(f"Server init successfully! {self.host}:{self.port}")
        except socket.error as e:
            print(f"Server init failed! {self.host}:{self.port}")
            traceback.print_exc()
        self.server.bind((self.host, self.port))
        self.server.listen(self.backlog)

    def _verify(self, cyphertext_recv):
        if self.cyphertext == cyphertext_recv:
            return True
        else:
            return False

    def listening(self):
        print("Server start listening...")

        tb_writer_dic = {}
        uts_tommrow = iTime.today().delta(days=1).uts()
        while True:
            datetime = iTime.now().datetime_str()
            if iTime.now().delta(minutes=config.interval).uts() > uts_tommrow:
                uts_tommrow = iTime.today().delta(days=1).uts()
                tb_writer_dic = {}
            try:
                cli, addr = self.server.accept()
                log_head = f"{datetime}| Server| {config.server_host} Clent| {addr[0]:>16s}:{str(addr[1]):>5s}|"
            except Exception as e:
                print(f"{datetime}| Server| Error occured when server accept datas. ")
                traceback.print_exc()
            try:
                recv_dic = cli.recv(self.buf_size).decode()
                recv_dic = json.loads(recv_dic)
                cyphertext = recv_dic.pop('cyphertext')
                if self._verify(cyphertext):
                    utils.save_stat(recv_dic, config.stat_log_dir)
                    cli_hostname = addr[0]
                    date = iTime(recv_dic['datetime']).date_str()
                    cli_tb_log_dir = osp.join(config.tb_log_dir, cli_hostname, date)
                    os.makedirs(cli_tb_log_dir, exist_ok=True)
                    if cli_hostname not in tb_writer_dic:
                        gpu_count = sum([1 for k in recv_dic if 'gpu/' in k])
                        tb_writer_dic[cli_hostname] = utils.SysstatTB(cli_tb_log_dir, gpu_count)
                    tb_writer = tb_writer_dic[cli_hostname]
                    tb_writer.update(recv_dic)
                    print(f"{log_head} Transport system statics successfully.")
                    cli.send(utils.dic2byte({'state_code': '200'}))
                else:
                    print(f"{log_head} Authorization failed!")
                    cli.send(utils.dic2byte({'state_code': '401.1'}))
            except Exception as e:
                print(f"{log_head} occur errors while processing received data!")
                cli.send(utils.dic2byte({'state_code': '502'}))
                traceback.print_exc()
            finally:
                cli.close()
