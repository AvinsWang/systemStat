import json
import socket
import utils
import logging
import client_config


client_log = logging.getLogger(client_config.client_log_name)


class ClientSocket:
    def __init__(self, host, port, backlog=5, buf_size=1024):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.client = None

    def init_client(self):
        try:
            self.client = socket.socket()
            self.client.connect((self.host, self.port))
        except:
            client_log.exception(f"Init clinet {self.host}:{self.port} failed!")
            exit()

    def close_client(self):
        if isinstance(self.client, socket.socket):
            self.client.close()
            self.client = None

    def send_msg(self, msg, plaintext):
        try:
            msg.update({'cyphertext': utils.gen_cyphertext(plaintext)})
            msg = json.dumps(msg)
            try:
                self.client.send(msg.encode('utf-8'))
                recv = self.client.recv(self.buf_size)
                return recv
            except:
                client_log.error('Sent statics failed!')
        except:
            client_log.error('Dump statics(python dict) to json failed!')
            return None
