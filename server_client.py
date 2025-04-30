import socket
from protocol import ProtocolHandler

class TupleClient:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def send_command(self, cmd):
     
        msg = ProtocolHandler.generate_response(cmd)
        self.sock.sendall(msg)
        header = self.sock.recv(3)
        if not header.isdigit():
            return "ERR invalid response"
        msg_length = int(header)
        response = self.sock.recv(msg_length).decode('utf-8')
        return response

if __name__ == "__main__":
    client = TupleClient('localhost', 5000)
    print(client.send_command("PUT key1 value1")) 