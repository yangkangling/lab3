import socket
import sys

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
   
    if len(sys.argv) != 4: 
        print("Usage: client.py <host> <port> <request_file>")
        return

    host = sys.argv[1]
    port_str = sys.argv[2]  
    filename = sys.argv[3]

    
    try:
        port = int(port_str)
    except ValueError:
        print(f"Error: Port number must be an integer (current value:{port_str})")
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.connect((host, port))
            with open(filename, 'r', encoding='utf-8') as f:
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if not parts:
                        print(f"Ignoring empty line: {line}")
                        continue
                    cmd = parts[0].upper()
                    error = False
                    if cmd == 'PUT':
                        if len(parts) < 3:
                            print(f"Invalid PUT command: {line}")
                            error = True
                        else:
                            key = parts[1]
                            value = ' '.join(parts[2:])
                            if len(key) > 999 or len(value) > 999 or (len(key) + 1 + len(value)) > 970:
                                print(f"Invalid PUT command: {line} (length exceeds)")
                                error = True
                    elif cmd in ('GET', 'READ'):
                        if len(parts) < 2:
                            print(f"Invalid {cmd} command: {line}")
                            error = True
                        else:
                            key = parts[1]
                            if len(key) > 999:
                                print(f"Invalid {cmd} command: {line} (key too long)")
                                error = True
                    else:
                        print(f"Unknown command: {line}")
                        error = True
                    if error:
                        continue
                    if cmd == 'PUT':
                        request = f"PUT {key} {value}\n"
                    elif cmd == 'GET':
                        request = f"GET {key}\n"
                    else:
                        request = f"READ {key}\n"
                    s.sendall(request.encode('utf-8'))
                    response = s.recv(1024).decode('utf-8').strip()
                    print(f"{request.strip()}: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()