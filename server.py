import socketserver
import threading

class TupleSpaceServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuples = {}
        self.lock = threading.Lock()

    def process_line(self, line):
        parts = line.strip().split()
        if not parts:
            return "ERR invalid request"
        
        cmd = parts[0].upper()
        if cmd == 'PUT':
            if len(parts) < 3:
                return "ERR invalid PUT command"
            
            key = parts[1]
            value = ' '.join(parts[2:])
            if len(key) > 999 or len(value) > 999 or (len(key) + 1 + len(value)) > 970:
                return f"ERR {key} invalid length"
            
            with self.lock:
                if key in self.tuples:
                    return f"ERR {key} already exists"
                self.tuples[key] = value
                return f"OK({key},{value})added"  
        
        elif cmd in ('GET', 'READ'):
            if len(parts) < 2:
                return f"ERR invalid {cmd} command"
            
            key = parts[1]
            if len(key) > 999:
                return f"ERR {key} invalid length"
            
            with self.lock:
                if key not in self.tuples:
                    return f"ERR {key} does not exist"
                
                if cmd == 'GET':
                    value = self.tuples.pop(key)
                    return f"OK({key},{value})removed"
                else:
                    value = self.tuples[key]
                    return f"OK({key},{value})read"
        
        else:
            return "ERR unknown command"

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = b''
            while True:
                chunk = self.request.recv(1)
                if not chunk or chunk == b'\n':
                    break
                data += chunk
            
            if not data:
                break
            
            line = data.decode('utf-8').strip()
            response = self.server.process_line(line)
            self.request.sendall(response.encode('utf-8') + b'\n')

if __name__ == "__main__":
    HOST, PORT = 'localhost', 9999
    server = TupleSpaceServer((HOST, PORT), RequestHandler)
    print(f"Server running on {HOST}:{PORT}")
    server.serve_forever()