import socket

def protocol_client(host, port, command):
    try:
        msg = f"{len(command):03d} {command}"
        with socket.create_connection((host, port), timeout=5) as s:
            s.sendall(msg.encode())
            
            header = s.recv(4)
            if len(header) < 4:
                return "ERR invalid response header"
                
            resp_length = int(header[:3])
            data = s.recv(resp_length)
            return data.decode()
            
    except Exception as e:
        return f"ERR ClientError: {str(e)}"

if __name__ == "__main__":
    print(protocol_client("localhost", 5000, "PUT test1 value1"))
