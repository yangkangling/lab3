import socket
class TupleClient:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)  
        try:
            self.sock.connect((host, port))
        except Exception as e:
            print(f"Connection failed: {str(e)}")

    def send_command(self, cmd):
        try:
            
            self.sock.sendall(cmd.encode('utf-8'))
            response = self.sock.recv(1024).decode('utf-8')
            return response
        except Exception as e:
            return f"ERR: {str(e)}"
if __name__ == "__main__":
    client = TupleClient('localhost', 5000)
    print(client.send_command("PUT key1 value1")) 
