import json
import os
import socket
import logging
import traceback
import os.path as osp
from itime import iTime

import utils
import server_config, client_config


server_log = logging.getLogger(server_config.server_log_name)


class ServerSocket:
    def __init__(self, host, port, cyphertext, backlog=128, buf_size=1024):
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
            self.server.bind((self.host, self.port))
            self.server.listen(self.backlog)
            server_log.info(f"Server init successfully! {self.host}:{self.port}")
        except socket.error as e:
            server_log.exception(f"Server init failed! {self.host}:{self.port}")
        
    def _verify(self, cyphertext_recv):
        if self.cyphertext == cyphertext_recv:
            return True
        else:
            return False

    def listening(self):
        print("Server start listening...")
        server_log.info("Server start listening...")

        tb_writer_dic = {}
        uts_tomorrow = iTime.today().delta(days=1).uts()
        while True:
            if iTime.now().delta(minutes=client_config.interval).uts() > uts_tomorrow:
                uts_tomorrow = iTime.today().delta(days=1).uts()
                tb_writer_dic = {}
            try:
                cli, addr = self.server.accept()
            except Exception:
                try:
                    server_log.exception(f"CLIENT [{addr[0]}:{str(addr[1])}] Error occured on accepting data!!")
                    cli.send(utils.dic2byte({'state_code': '502'}))
                    traceback.print_exc()
                except Exception:
                    server_log.exception(f"Error occured on accepting data!!")
                    cli.send(utils.dic2byte({'state_code': '502'}))
                continue
            try:
                log_head = f"CLIENT [{addr[0]}:{str(addr[1])}]"
                try:
                    recv_dic = cli.recv(self.buf_size).decode()
                    try:
                        recv_dic = json.loads(recv_dic)
                    except Exception:
                        server_log.info(f"CAN'T decode Received [{recv_dic}] from {log_head}  as json!")
                        cli.send(utils.dic2byte({'state_code': '502'}))
                        continue
                    cyphertext = recv_dic.pop('cyphertext')
                    if self._verify(cyphertext):
                        utils.save_stat(recv_dic, server_config.stat_log_dir)
                        cli_hostname = addr[0]
                        if 'client_name' in recv_dic and recv_dic['client_name'] != '':
                            cli_hostname = recv_dic['client_name']
                        date = iTime(recv_dic['datetime']).date_str()
                        cli_tb_log_dir = osp.join(server_config.tb_log_dir, cli_hostname, date)
                        os.makedirs(cli_tb_log_dir, exist_ok=True)
                        if cli_hostname not in tb_writer_dic:
                            gpu_count = sum([1 for k in recv_dic if 'gpu/' in k])
                            tb_writer_dic[cli_hostname] = utils.SysstatTB(cli_tb_log_dir, gpu_count)
                        tb_writer = tb_writer_dic[cli_hostname]
                        tb_writer.update(recv_dic)
                        server_log.info(f"Received from {log_head} successfully.")
                        cli.send(utils.dic2byte({'state_code': '200'}))
                    else:
                        server_log.info(f"{log_head} Authorization failed!")
                        cli.send(utils.dic2byte({'state_code': '401.1'}))
                    cli.close()
                except Exception:
                    cli.send(utils.dic2byte({'state_code': '502'}))
                    server_log.exception(f"{log_head} occur errors while processing received data!")
            except Exception as e:
                server_log.exception(f"Server occurred error when server accepting datas. ")
