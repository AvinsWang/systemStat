import socket
import argparse
import client_config


def get_args():
    parser = argparse.ArgumentParser(description='Test connection')
    parser.add_argument('--host', type=str)
    parser.add_argument('--port', type=int)
    parser.add_argument('--msg', type=str)
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    if not args.host or not args.port:
        args.host = client_config.server_host
        args.port = client_config.server_port

    client = socket.socket()
    client.connect((args.host, args.port))

    print('Connect success!', f"{args.host}:{args.port}")
    if args.msg:
        client.send(args.msg.encode('utf-8'))
        recv = client.recv(1024).decode()
        print(f"Sent: {args.msg}, Recv: {recv}")
    client.close()