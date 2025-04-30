import subprocess
import time
import os
import socket
import socketserver


class TupleSpaceServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = TURE 


def wait_for_port(port, timeout=10):
    """ Waiting for the port to become connectable """
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket() as s:
                s.connect(('localhost', port))
                return True
        except ConnectionRefusedError:
            time.sleep(0.5)
    return False

def run_test(client_args, expected_lines):
    server_process = subprocess.Popen(["python", "server.py", "9999"])

    result = subprocess.run(
        client_args,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    print("Actual client output:\n", result.stdout) 
    print("Client error message:\n", result.stderr)


    server_process = subprocess.Popen(
        ["python", "server_client.py", "localhost", "9999", "test_requests.txt"],
        stderr=subprocess.DEVNULL
    )
    
    try:
       
        if not wait_for_port(9999):
            raise RuntimeError("Server startup failed, port not listening")
        
        result = subprocess.run(
            client_args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15
        )
       
        print("[Server stdout]\n" + result.stdout)
        print("[Server stderr]\n" + result.stderr)
       
        output = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        
        assert len(output) == len(expected_lines), f"expect{len(expected_lines)}line,actual{len(output)}line"
        for act, exp in zip(output, expected_lines):
            assert act == exp, f"expect '{exp}',actual '{act}'"
            
    finally:
        server_process.terminate()

assert os.path.exists("test_requests.txt"), "Error: The requested file does not exist!"



def check_port(port):
    result = subprocess.run(
        ["netstat", "-ano"], 
        capture_output=True, 
        text=True
    )
    lines = result.stdout.split('\n')
    return any(f":{port}" in line for line in lines)

if check_port(5000):
    print("Port 5000 is already in use.")
else:

    print("Port 5000 is available.")

run_test(
    ["python", "server_client.py", "localhost", "9999", "test_requests.txt"],
    [
        "PUT key1 value1:OK(key1,value1)added",
        "PUT key2 value2:OK(key2,value2)added",
        "READ key1:OK(key1,value1)read",
        "GET key2:OK(key2,value2)removed",
        "READ key3:ERRkey3doesnotexist",
        "PUT key1 new_value1:ERRkey1alreadyexists"
    ]
)