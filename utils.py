import os
import json
import logging
import hashlib
import traceback
import subprocess
import os.path as osp
from itime import iTime
from tensorboardX import SummaryWriter

import server_config, client_config

# if iTime not found, do
# pip install py-itime


class Logger:
    def __init__(self, name, log_path=None, level=logging.INFO):
        log_dir = osp.dirname(log_path)
        os.makedirs(log_dir, exist_ok=True)
        self._logger = logging.getLogger(name)
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s %(filename)s %(lineno)s |%(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(level)

    def info(self, msg):
        if self._logger is not None:
            self._logger.info(msg)

    def warning(self, msg):
        if self._logger is not None:
            self._logger.warning(msg)

    def exception(self, e):
        if self._logger is not None:
            self._logger.exception(e)


Logger(server_config.server_log_name, log_path=server_config.server_log_path)
Logger(client_config.client_log_name, log_path=client_config.client_log_path)

client_log = logging.getLogger(client_config.client_log_name)


def exec_shell(cmd):
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = res.stdout.read()
    res.wait()
    res.stdout.close()
    return result


def gen_cyphertext(plaintext):
    return hashlib.md5(plaintext.encode('utf-8')).hexdigest()


def save_stat(stat_dic, stat_save_dir):
    host = stat_dic['hostname']
    date = stat_dic['datetime'].split()[0]
    sub_dir = osp.join(stat_save_dir, host)
    os.makedirs(sub_dir, exist_ok=True)
    log_fpath = osp.join(sub_dir, date)

    with open(log_fpath, 'a+') as f:
        f.write(json.dumps(stat_dic) + '\n')


class SysstatTB:
    def __init__(self, tb_log_dir, gpu_count):
        self.gpu_count = gpu_count

        cm_lis = ["cm/cp", "cm/mp"]
        disk_lis = ["disk/dp", "disk/dr", "disk/dw"]
        net_lis = ["net/ns", "net/nr"]
        # auto generate layout
        gpu_key_map = dict()
        gpu_perc_lis = list()
        gpu_mem_perc_lis = list()
        for i in range(gpu_count):
            key = f"gpu/{i}"
            gpu_key_map[key] = {'perc': 'perc', 'mem_perc': 'mem_perc'}
            gpu_perc_lis.append(f"gpu_perc/{i}")
            gpu_mem_perc_lis.append(f"gpu_mem_perc/{i}")
        layout = {
            "sysstat": {
                "cm": ["Multiline", cm_lis],
                "disk": ["Multiline", disk_lis],
                "net": ["Multiline", net_lis],
                "gpu_perc": ["Multiline", gpu_perc_lis],
                "gpu_mem_perc": ["Multiline", gpu_perc_lis]
            }
        }

        self.scaler_key_lis = [*cm_lis, *disk_lis, *net_lis, *list(gpu_key_map.keys())]

        self.writer = SummaryWriter(logdir=tb_log_dir)
        self.writer.add_custom_scalars(layout)

    def update(self, data_dic):
        datatime = data_dic['datetime']
        hour = iTime(datatime).strf('%H')
        minute = iTime(datatime).strf('%M')
        hm_dec = float(hour) + float(minute) / 60
        step = int(hm_dec * 100)
        for scl_key in self.scaler_key_lis:
            if 'gpu' not in scl_key:
                self.writer.add_scalar(scl_key, data_dic[scl_key], global_step=step)
            else:
                gpu_dic = data_dic[scl_key]
                self.writer.add_scalar(f"gpu_perc/{gpu_dic['index']}", gpu_dic['perc'], global_step=step)
                self.writer.add_scalar(f"gpu_mem_perc/{gpu_dic['index']}", gpu_dic['mem_perc'], global_step=step)


def check_server_return_state(state_dic):
    state_dic = state_dic.decode()
    state_dic = json.loads(state_dic)
    state_code = str(state_dic['state_code'])
    if state_code == '200':
        client_log.info(f"[{state_code}] Sent system statics successfully!")
    elif state_code == '401.1':
        client_log.error(f"[{state_code}] Authorization failed!")
    elif state_code == '502':
        client_log.error(f"[{state_code}] Sever internal error!")
    else:
        client_log.error(f"[{state_code}] Undefined state code.")


def dic2byte(dic):
    try:
        return json.dumps(dic).encode()
    except:
        traceback.print_exc()
        return b'state_code: 000'
