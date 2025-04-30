import subprocess
import time
import os
import socket
import socketserver

def get_free_port():
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def wait_for_port(port, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket() as s:
                s.settimeout(1)
                s.connect(('localhost', port))
                return True
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.5)
    return False

def run_test(client_args, expected_lines):
    test_port = get_free_port()
    server_process = None
    try:
        server_process = subprocess.Popen(
            ["python", "server.py", str(test_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        if not wait_for_port(test_port, 20):
            server_stdout, server_stderr = server_process.communicate()
            print(f"[Server Log] stdout:\n{server_stdout}")
            print(f"[Server Log] stderr:\n{server_stderr}")
            raise RuntimeError("Serverstarttimeout")
     
        client_result = subprocess.run(
            client_args[:-2] + [str(test_port), client_args[-1]], 
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=20
        )
        
        server_stdout, server_stderr = server_process.communicate()
        print(f"[Server Log] stdout:\n{server_stdout}")
        print(f"[Server Log] stderr:\n{server_stderr}")
        
        client_output = [line.strip() for line in client_result.stdout.splitlines() if line.strip()]
        assert len(client_output) == len(expected_lines), \
            f"expect{len(expected_lines)} line,actual{len(client_output)}line."
        for actual, expected in zip(client_output, expected_lines):
            assert actual == expected, f"expect:{expected}\nactual:{actual}"
            
        print("✅ alltestspassed")
    except Exception as e:
        print(f"❌ testsfailed{str(e)}")
        raise
    finally:
        if server_process:
            server_process.terminate()

if __name__ == "__main__":
    if not os.path.exists("test_requests.txt"):
        print("Error: Missing test file test_requests.txt")
        os._exit(1)
    run_test(
        ["python", "server_client.py", "localhost", "test_requests.txt"],  
        [
            "PUT key1 value1:OK(key1,value1)added",
            "PUT key2 value2:OK(key2,value2)added",
            "READ key1:OK(key1,value1)read",
            "GET key2:OK(key2,value2)removed",
            "READ key3:ERRkey3doesnotexist",
            "PUT key1 new_value1:ERRkey1alreadyexists"
        ]
    )