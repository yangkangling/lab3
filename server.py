import socketserver
import socket
from tuple_space import TupleSpace
from protocol import ProtocolHandler

class TupleSpaceServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuple_space = TupleSpace()
        self.protocol = ProtocolHandler()

class RequestHandler(socketserver.BaseRequestHandler):
    buffer = b''

    def handle(self):
        while True:
            try:
                data = self.request.recv(1024)
                if not data:
                    break
                self.buffer += data

                while True:
                 
                    full_msg, remaining = ProtocolHandler.parse_request(self.buffer)
                    if full_msg is None:
                        break

                    self.buffer = remaining
               
                    response = self.process_command(full_msg)
                
                    self.request.sendall(response)

            except (ConnectionResetError, BrokenPipeError):
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
    HOST, PORT = 'localhost', 5000
    try:
        server = TupleSpaceServer((HOST, PORT), RequestHandler)
        print(f"[STATUS] Server started at {HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"[FATAL] Server failed to start: {str(e)}")
    finally:
        server.shutdown()
