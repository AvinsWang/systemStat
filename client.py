import json
import socket
import utils
import logging
import config


client_log = logging.getLogger(config.client_log_name)


class ClientSocket:
    def __init__(self, host, port, backlog=5, buf_size=1024):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.client = None

    def init_client(self):
        self.client = socket.socket()
        self.client.connect((self.host, self.port))

    def close_client(self):
        if isinstance(self.client, socket.socket):
            self.client.close()
            self.client = None

    def send_msg(self, msg, plaintext):
        try:
            msg.update({'cyphertext': utils.gen_cyphertext(plaintext)})
            msg = json.dumps(msg)
            self.client.send(msg.encode('utf-8'))
            recv = self.client.recv(self.buf_size)
            return recv
        except:
            return ''
