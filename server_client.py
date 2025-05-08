import socket
import threading
import time
from collections import defaultdict

class TupleSpaceServer:
    def __init__(self):
        self.tuple_space = {}
        self.lock = threading.Lock()
        self.stats = {
            'total_clients': 0,
            'total_ops': 0,
            'reads': 0,
            'gets': 0,
            'puts': 0,
            'errors': 0,
            'start_time': time.time()
        }
        self.running = True

    def handle_client(self, conn, addr):
        with conn:
            self.stats['total_clients'] += 1
            print(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(1024).decode().strip()
                    if not data:
                        break
                    self.process_request(conn, data)
                except Exception as e:
                    print(f"Error handling client {addr}: {e}")
                    break
            print(f"Disconnected: {addr}")

    def process_request(self, conn, raw_data):
        try:
            msg_length = int(raw_data[:3])
            cmd = raw_data[4]
            msg_body = raw_data[5:]
            key = ""
            value = ""
            if cmd == 'P':
                split_index = msg_body.find(' ')
                if split_index == -1:
                    key = msg_body
                    value = ""
                else:
                    key = msg_body[:split_index]
                    value = msg_body[split_index+1:]
            else:
                key = msg_body
                value = ""

            response = ""
            with self.lock:
                self.stats['total_ops'] += 1
                if cmd == 'R':
                    self.stats['reads'] += 1
                    if key in self.tuple_space:
                        v = self.tuple_space[key]
                        msg_content = f"OK ({key}, {v}) read"
                        response = f"{len(msg_content):03d} {msg_content}"
                    else:
                        msg_content = f"ERR {key} does not exist"
                        response = f"{len(msg_content):03d} {msg_content}"
                        self.stats['errors'] += 1
                elif cmd == 'G':
                    self.stats['gets'] += 1
                    if key in self.tuple_space:
                        v = self.tuple_space.pop(key)
                        msg_content = f"OK ({key}, {v}) removed"
                        response = f"{len(msg_content):03d} {msg_content}"
                    else:
                        msg_content = f"ERR {key} does not exist"
                        response = f"{len(msg_content):03d} {msg_content}"
                        self.stats['errors'] += 1
                elif cmd == 'P':
                    self.stats['puts'] += 1
                    if key not in self.tuple_space:
                        if not key or not value:
                            msg_content = "ERR key or value cannot be empty"
                            response = f"{len(msg_content):03d} {msg_content}"
                            self.stats['errors'] += 1
                        elif len(key) + len(value) > 970:
                            msg_content = "ERR key-value too long"
                            response = f"{len(msg_content):03d} {msg_content}"
                            self.stats['errors'] += 1
                        else:
                            self.tuple_space[key] = value
                            msg_content = f"OK ({key}, {value}) added"
                            response = f"{len(msg_content):03d} {msg_content}"
                    else:
                        msg_content = f"ERR {key} already exists"
                        response = f"{len(msg_content):03d} {msg_content}"
                        self.stats['errors'] += 1
                else:
                    msg_content = "ERR invalid command"
                    response = f"{len(msg_content):03d} {msg_content}"
                    self.stats['errors'] += 1

            conn.sendall(response.encode())
        except Exception as e:
            error_msg_content = "ERR internal error"
            error_msg = f"{len(error_msg_content):03d} {error_msg_content}"
            conn.sendall(error_msg.encode())
            print(f"Error processing request: {e}")

    def start_statistics(self):
        while self.running:
            time.sleep(10)
            with self.lock:
                total_tuples = len(self.tuple_space)
                avg_key = sum(len(k) for k in self.tuple_space)/total_tuples if total_tuples else 0
                avg_value = sum(len(v) for v in self.tuple_space.values())/total_tuples if total_tuples else 0
                print(f"""
=== Server Statistics ===
Tuples: {total_tuples}
Average Key Size: {avg_key:.2f}
Average Value Size: {avg_value:.2f}
Total Clients: {self.stats['total_clients']}
Total Operations: {self.stats['total_ops']}
READs: {self.stats['reads']}
GETs: {self.stats['gets']}
PUTs: {self.stats['puts']}
Errors: {self.stats['errors']}
Uptime: {time.time() - self.stats['start_time']:.2f}s
========================""")
    def start_server(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('localhost', port))
            s.listen()
            print(f"Server listening on port {port}")
            stats_thread = threading.Thread(target=self.start_statistics)
            stats_thread.start()
            try:
                while True:
                    conn, addr = s.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                    client_thread.start()
            except KeyboardInterrupt:
                self.running = False
                stats_thread.join()
                print("Server shutdown.")

if __name__ == "__main__":
    port = 5123 
    server = TupleSpaceServer()
    server.start_server(port)
