import threading

class TupleSpace:
    def __init__(self):
        self._tuples = {}  
        self._lock = threading.Lock()  
    
    def put(self, key, value):
        
        # Verify the total length of key values
        if (len(key) + len(value) + 1) > 970:  
            return False, f"ERR key-value too long"
        
        with self._lock:  
            if key in self._tuples:
                return False, f"ERR {key} already exists"
            else:
                self._tuples[key] = value
                return True, f"OK ({key}, {value}) added"
    
    def get(self, key):
        """Delete and return the value corresponding to the key"""
        with self._lock:
            if key not in self._tuples:
                return False, f"ERR {key} does not exist"
            else:
                value = self._tuples.pop(key)
                return True, f"OK ({key}, {value}) removed"
    
    def read(self, key):
        """Read the value corresponding to the key (without deleting)"""
        with self._lock:
            if key not in self._tuples:
                return False, f"ERR {key} does not exist"
            else:
                value = self._tuples[key]
                return True, f"OK ({key}, {value}) read"

    @property
    def size(self):
        """Current number of tuples (for testing purposes)"""
        with self._lock:
            return len(self._tuples)
    







