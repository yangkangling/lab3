import socket

def protocol_client(host, port, command):
    
    msg = f"{len(command):03d} {command}"
    
    with socket.socket() as s:
        s.connect((host, port))
        s.sendall(msg.encode('utf-8'))
        
       
        header = s.recv(4)  
        resp_length = int(header[:3])
        data = s.recv(resp_length)
        return data.decode()

if __name__ == "__main__":
    print(protocol_client("localhost", 5000, "PUT key1 value1")) 
