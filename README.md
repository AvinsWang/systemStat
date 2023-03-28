# systemStat
A simple B/S python program for collecting and displaying system information

## Demo
![demo_img](demo.png)

## Glossary
cm: cpu & memory
- cm/cp: cpu utilization percentage
- cm/cp: memory utilization percentage

disk: 
- disk/dp: disk utilization percentage
- disk/dr: disk read(MB/s)
- disk/dw: disk write(MB/s)

gpu_mem_prec: gpu memory utilization percentage
- gpu_mem_prec/0: gpu memory utilization percentage on gpu 0

gpu_perc: gpu utilization percentage
- gpu_perc/0: gpu utilization percentage on gpu 0

net: network
- net/nr: network read(MB/s)
- net/nw: network write(MB/s)

## How to use
### Set & Launch Server
- make worksapce  
```shell
mkdir /etc/systemStat
```
- clone or download the repo
```shell
cd /etc/systemStat
git clone git@github.com:AvinsWang/systemStat.git
```

- Install requriments  
```shell
pip install -r requriments.txt
```

- set server_config
```python
# === server setting ===
# echo -n your_plaintext | md5sum
server_cyphertext = '4ca53a363c7890e1cff6264c4a824a64'
# to save system statics json
stat_log_dir = '/etc/systemStat/systemStat/logs/stat'
# to save tensorboard log
tb_log_dir = '/etc/systemStat//systemStat/logs/tb'
# to save server log
server_log_path = '/etc/systemStat/systemStat/logs/server.log'
# server log name
server_log_name = 'systemStat_server'
# server host and port to be exposed to clients
server_host = ''
server_port = 8008

```
4. launch server  
```shell
python main.py --server
```

### Set & Lanuch Tensorboard Server
```shell
# launch tensorboard server on background
python main.py --tb_server --bg
# or, specify tensorboard port
pythom main.py --tb_port 8008 -bg
```
**Notice: server and tb_server should be launched on same machine**

### Set & Launch Client
- set client_config.py
```python
# === client setting ===
# client send data to server host & port
# host and port for client connect to server
client_log_path = '/etc/systemStat/logs/client.log'
client_log_name = 'systemStat_client'
# The host & port to be connected
server_host = '127.0.0.1'
server_port = 8008
# the name to identify this client, DO NOT repeat
client_name = 'test_server'
# send statics from client to server interval, minutes
interval = 1
```

```shell
# add a task on crontab
# notice: 
# 1. your planetext should same to the plaintext which convert(md5) to config.py server_cyphertext
# 2. the interval for send statics form client to server should same to config.py interval
# e.g. interval=1, every one minute send to server
* * * * * python3 /etc/systemStat/systemStat/main.py --client --plaintext your_planetext
```

## Acknowledgment
Thanks for [gpustat](https://github.com/wookayin/gpustat) great work!