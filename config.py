# === server setting ===
# echo -n your_plaintext | md5sum
server_cyphertext = '4ca53a363c7890e1cff6264c4a824a64'
# to save system statics json
stat_log_dir = '/etc/systemStat/logs/stat'
# to save tensorboard log
tb_log_dir = '/etc/systemStat/logs/tb'
# to save server log
server_log_path = '/etc/systemStat/logs/server.log'
# server log name
server_log_name = 'systemStat_server'
# server host and port to be exposed to clients
server_host = "3a17ebe52abf"
server_port = 6012


# === client setting ===
# client send data to server host & port
# host and port for client connect to server
client_log_path = '/etc/systemStat/logs/client.log'
client_log_name = 'systemStat_client'
server_host = "3a17ebe52abf"
server_port = 6012
# the name to identify client
client_name = '69'
# send statics from client to server interval, minutes
interval = 1