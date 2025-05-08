from TupleSpace import TupleSpace
def test_tuplespace():
    ts = TupleSpace()
    
    # Test PUT
    success, msg = ts.put("name", "Alice")
    assert success and "added" in msg
    
    # Test repeated PUT
    success, msg = ts.put("name", "Bob")
    assert not success and "already exists" in msg
    
    # Test READ
    success, msg = ts.read("name")
    assert success and "Alice" in msg
    
    # Test GET
    success, msg = ts.get("name")
    assert success and "removed" in msg
    
    # Test reading non-existent keys
    success, msg = ts.read("invalid")
    assert not success and "does not exist" in msg
    
    print("All tests passed!")

if __name__ == "__main__":
    test_tuplespace()
