import time
import platform
import psutil as pu
from itime import iTime
import gpustat_local
import utils

# psutil doc
# https://psutil.readthedocs.io/en/latest/


B2KB = 1024.
B2MB = B2KB * 1024.
B2GB = B2MB * 1024.


# === func ===
def hostname():
    return {'hostname': platform.node()}


def cpu_perc():
    return {'cm/cp': pu.cpu_percent()}


def mem_perc():
    return {'cm/mp': pu.virtual_memory().percent}


def disk_perc(path='/'):
    return {'disk/dp': pu.disk_usage(path).percent}


def disk_io_speed():
    pre = pu.disk_io_counters(perdisk=False, nowrap=True)
    time.sleep(1)
    nex = pu.disk_io_counters(perdisk=False, nowrap=True)
    read = round((nex.read_bytes - pre.read_bytes) / B2MB, 5)
    write = round((nex.write_bytes - pre.write_bytes) / B2MB, 5)
    return {'disk/dr': read, 'disk/dw': write}


def net_io_speed():
    pre = pu.net_io_counters(pernic=False, nowrap=True)
    time.sleep(1)
    nex = pu.net_io_counters(pernic=False, nowrap=True)
    sent = round((nex.bytes_sent - pre.bytes_sent) / B2MB, 5)
    recv = round((nex.bytes_recv - pre.bytes_recv) / B2MB, 5)
    return {'net/ns': sent, 'net/nr': recv}


def gpu_perc_mem():
    # gpu usage and memery
    raw_dic = gpustat_local.get_gpu_info()
    gpu_raw_lis = raw_dic['gpus']
    gpu_dic = dict()
    for _gpu_dic in gpu_raw_lis:
        _dic = \
            {
                'index': _gpu_dic['index'],
                'temp': _gpu_dic['temperature.gpu'],
                'perc': _gpu_dic['utilization.gpu'],
                'power_prec': round(_gpu_dic['power.draw'] / _gpu_dic['enforced.power.limit'] * 100, 2),
                'mem_perc': round(_gpu_dic['memory.used'] / _gpu_dic['memory.total'] * 100, 2)
            }
        gpu_dic[f"gpu/{_gpu_dic['index']}"] = _dic
    return gpu_dic


def sysstat():
    """
    system static
    :return:
    {"hostname": "3a17ebe52abf",
    "datetime": "2022-09-21 20:53:03",
    "cm/cp": 11.5,          # cpu utilization
    "cm/mp": 45.8,          # memory utilization
    "disk/dp": 4.8,         # disk usage/total
    "disk/dr": 23.75,       # disk read  MB/s
    "disk/dw": 0.0,         # disk write MB/s
    "net/ns": 0.0,          # net sent  MB/s
    "net/nr": 0.0,          # net recv  MB/s
    # gpu_key, index,   temperature,  utilization,  power,              memory utilization
    "gpu/0": {"index": 0, "temp": 54, "perc": 100, "power_prec": 71.43, "mem_perc": 98.38},
    "gpu/1": {"index": 1, "temp": 53, "perc": 100, "power_prec": 65.14, "mem_perc": 98.38},
    "gpu/2": {"index": 2, "temp": 52, "perc": 0,   "power_prec": 47.43, "mem_perc": 98.38},
    "gpu/3": {"index": 3, "temp": 52, "perc": 100, "power_prec": 62.86, "mem_perc": 98.38},
    "gpu/4": {"index": 4, "temp": 52, "perc": 100, "power_prec": 58.29, "mem_perc": 98.39},
    "gpu/5": {"index": 5, "temp": 53, "perc": 100, "power_prec": 57.71, "mem_perc": 98.38},
    "gpu/6": {"index": 6, "temp": 60, "perc": 75,  "power_prec": 83.43, "mem_perc": 95.63},
    "gpu/7": {"index": 7, "temp": 54, "perc": 99,  "power_prec": 82.0,  "mem_perc": 95.64}}
    """
    sysstat_info = hostname()
    sysstat_info['datetime'] = iTime.now().datetime_str()
    gen_info = dict()  # cpu mem dis net, exclude gpu
    gen_info.update(cpu_perc())
    gen_info.update(mem_perc())
    gen_info.update(mem_perc())
    gen_info.update(disk_perc())
    gen_info.update(disk_io_speed())
    gen_info.update(net_io_speed())
    sysstat_info.update(gen_info)
    sysstat_info.update(gpu_perc_mem())
    return sysstat_info
