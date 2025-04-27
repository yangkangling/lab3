import socket
import sys

# 强制 Python 使用 UTF-8 编码（添加到脚本开头）
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    if len(sys.argv) != 2:
        print("Usage: client.py <request_file>")
        return
    filename = sys.argv[1]
    host = 'localhost'
    port = 9999

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            with open(filename, 'r', encoding='utf-8') as f:  # 显式指定文件编码
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
                    s.sendall(request.encode('utf-8'))  # 显式指定发送编码
                    response = s.recv(1024).decode('utf-8').strip()  # 显式指定接收编码
                    print(f"{request.strip()}: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()