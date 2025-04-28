import socketserver
import threading
import socket 

class TupleSpaceServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 新增这行
        super().server_bind()

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
                    return f"ERR {key}alreadyexists"
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
                    return f"ERR {key}doesnotexist"
                
                if cmd == 'GET':
                    value = self.tuples.pop(key)
                    return f"OK({key},{value})removed"
                else:
                    value = self.tuples[key]
                    return f"OK({key},{value})read"
        
        else:
            return "ERR unknown command"


class RequestHandler(socketserver.BaseRequestHandler):
    buffer = b''  
    def handle(self):
        while True:
            try:
                data = self.request.recv(1024)
                if not data:
                    break
                self.buffer += data

                while len(self.buffer) >= 4:
                    header = self.buffer[:4]
                    if not header[:3].isdigit():
                        break  
                    
                    msg_length = int(header[:3])
                    if len(self.buffer) >= 4 + msg_length:
                        
                        full_msg = self.buffer[4:4+msg_length]
                        self.buffer = self.buffer[4+msg_length:]
                        
                        line = full_msg.decode('utf-8').strip()
                        response = self.server.process_line(line)
                        response_msg = f"{len(response):03d} {response}"
                        self.request.sendall(response_msg.encode('utf-8'))
                    else:
                        break  
            except:
                break
    
if __name__ == "__main__":
    HOST, PORT = 'localhost', 5000
    try:
        server = TupleSpaceServer((HOST, PORT), RequestHandler)
        print(f"[STATUS] Server started at {HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"[FATAL] Server failed to start:{str(e)}")
    finally:
        server.shutdown()