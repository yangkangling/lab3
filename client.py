import socket

def send_request(host, port, key, value, cmd):
    if cmd == "PUT":
        msg = f"P {key} {value}"
    elif cmd == "GET":
        msg = f"G {key}"
    elif cmd == "READ":
        msg = f"R {key}"
    
    nnn = f"{len(msg):03d}"
    full_msg = f"{nnn} {msg}"
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(full_msg.encode())
        response = s.recv(1024).decode()
        print(response)

if __name__ == "__main__":

    send_request('localhost', 51234, 'name', 'Alice', 'PUT')
    send_request('localhost', 51234, 'name', '', 'READ')
    #send_request('localhost', 51234, 'name', '', 'GET')
