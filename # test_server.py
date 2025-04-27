import subprocess
import time
import os

def run_test(client_args, expected_lines):
    
    server_process = subprocess.Popen(["python", "server.py", "9999"])
    time.sleep(1)  
    
    try:
       
        result = subprocess.run(
            client_args,
            capture_output=True,
            text=True,
            encoding='utf-8'  
        )
        output = result.stdout.splitlines()
        
        assert len(output) == len(expected_lines), f"expect{len(expected_lines)}line,exact{len(output)}line"
        for line, expected in zip(output, expected_lines):
            assert line == expected, f"expect '{expected}',exact '{line}'"
            
    finally:
        server_process.terminate() 


assert os.path.exists("test_requests.txt"), "wrong:there is no such file"

run_test(
    ["python", "server_client.py", "localhost", "9999", "test_requests.txt"],
    [
        "PUT key1 value1: OK(key1,value1) added",
        "PUT key2 value2: OK(key2,value2) added",
        "READ key1: OK(key1,value1) read",
        "GET key2: OK(key2,value2) removed",
        "READ key3: ERR key3 does not exist",
        "PUT key1 new_value1: ERR key1 already exists"
    ]
)