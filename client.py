import sys  
import socketserver
import socket
import threading
import time
from TupleSpace import TupleSpace
from protocol_client import ProtocolHandler

class TupleSpaceServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.tuple_space = TupleSpace()
        self.stats = {
            'total_clients': 0,
            'total_ops': 0,
            'reads': 0,
            'gets': 0,
            'puts': 0,
            'errors': 0,
            'start_time': time.time()
        }
        self._stats_thread = threading.Thread(target=self._log_statistics)
        self._stats_thread.daemon = True
        self._stats_thread.start()
        def _log_statistics(self):
            """Output server statistics information every 10 seconds"""
        while True:
            time.sleep(10)
            with self.tuple_space._lock:  
                total_tuples = self.tuple_space.size
                avg_key = sum(len(k) for k in self.tuple_space._tuples) / total_tuples if total_tuples else 0
                avg_value = sum(len(v) for v in self.tuple_space._tuples.values()) / total_tuples if total_tuples else 0
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
class RequestHandler(socketserver.BaseRequestHandler):
    buffer = b''

    def handle(self):
        self.server.stats['total_clients'] += 1
        print(f"[DEBUG] New client connected. Total clients: {self.server.stats['total_clients']}")
        while True:
            try:
                data = self.request.recv(1024)
                if not data:
                    break
                self.buffer += data

                while True:
                    if len(self.buffer) < 3:
                        break

                    try:
                        msg_length_str = self.buffer[:3].decode()
                        msg_length = int(msg_length_str)
                    except (ValueError, UnicodeDecodeError):
                        
                        self.request.sendall(f"023 ERR invalid NNN prefix".encode())
                        self.buffer = b''
                        break

                    if len(self.buffer) < msg_length + 3:
                        break  

                    full_msg = self.buffer[3:3 + msg_length].decode()
                    self.buffer = self.buffer[3 + msg_length:]
                    print(f"[DEBUG] Parsed message: {full_msg}")
                    response = self.process_command(full_msg)
                    self.request.sendall(response.encode())

            except (ConnectionResetError, BrokenPipeError) as e:
                print(f"Client disconnected abruptly: {e}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

    def process_command(self, line):
        parts = line.strip().split()
        if not parts:
            return ProtocolHandler.generate_response("ERR invalid request")

        cmd = parts[0].upper()
        if cmd == 'PUT':
            if len(parts) < 3:
                return ProtocolHandler.generate_response("ERR invalid PUT command")
            key, value = parts[1], ' '.join(parts[2:])
            valid, err_msg = ProtocolHandler.validate_length(key, value)
            if not valid:
                return ProtocolHandler.generate_response(err_msg)
            success, response = self.server.tuple_space.put(key, value)
            return ProtocolHandler.generate_response(response)

        elif cmd in ('GET', 'READ'):
            if len(parts) < 2:
                return ProtocolHandler.generate_response(f"ERR invalid {cmd} command")
            key = parts[1]
            if len(key) > 999:
                return ProtocolHandler.generate_response(f"ERR {key} invalid length")
            if cmd == 'GET':
                success, response = self.server.tuple_space.get(key)
            else:
                success, response = self.server.tuple_space.read(key)
            return ProtocolHandler.generate_response(response)

        else:
            return ProtocolHandler.generate_response("ERR unknown command")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    HOST, PORT = '0.0.0.0', port 
    server =None
    try:
        server = TupleSpaceServer((HOST, PORT), RequestHandler)
        print(f"[STATUS] Server started at {HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"[FATAL] Server failed to start: {str(e)}")
    
