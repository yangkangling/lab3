import subprocess

def run_test(client_cmd, request_file, expected_lines):
    result = subprocess.run(
        [client_cmd, request_file],
        capture_output=True,
        text=True
    )
    output = result.stdout.splitlines()
    assert len(output) == len(expected_lines), f"Expected {len(expected_lines)} lines, got {len(output)}"
    for line, expected in zip(output, expected_lines):
        assert line == expected, f"Expected '{expected}', got '{line}'"

run_test(
    "python",
    "test_requests.txt",
    [
        "PUT key1 value1: OK (key1, value1) added",
        "PUT key2 value2: OK (key2, value2) added",
        "READ key1: OK (key1, value1) read",
        "GET key2: OK (key2, value2) removed",
        "READ key3: ERR key3 does not exist",
        "PUT key1 new_value1: ERR key1 already exists"
    ]
)
