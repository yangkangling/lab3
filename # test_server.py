import subprocess
import time
import os
import socket

def wait_for_port(port, timeout=10):
    """ Waiting for the port to become connectable """
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', port))
                return True
        except ConnectionRefusedError:
            time.sleep(0.5)
    return False

def run_test(client_args, expected_lines):
   
    server_process = subprocess.Popen(
        ["python", "server.py", "9999"],
        stderr=subprocess.DEVNULL
    )
    
    try:
        
        if not wait_for_port(9999):
            raise RuntimeError("服务器启动超时")
       
        result = subprocess.run(
            client_args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15  
        )
        
        output = result.stdout.splitlines()
        print("实际客户端输出：")  
        for line in output:
            print(f"> {line}")
        
    
        assert len(output) == len(expected_lines), f"expect{len(expected_lines)}line , exact{len(output)}line."
        for line, expected in zip(output, expected_lines):
            assert line.strip() == expected.strip(), f"expect '{expected}',exact '{line}'"
            
    finally:
        server_process.terminate()

assert os.path.exists("test_requests.txt"), "wrong:test_requests.txt file doesn't exist."

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