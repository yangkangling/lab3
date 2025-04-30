import threading

class TupleSpace:
    def __init__(self):
        self.tuples = {}
        self.lock = threading.Lock()

    def put(self, key, value):
        """Add key value pairs, return operation results and response messages"""
        with self.lock:
            if key in self.tuples:
                return False, f"ERR {key}alreadyexists"
            self.tuples[key] = value
            return True, f"OK({key},{value})added"

    def get(self, key):
        """Delete and return key value pairs, return error if none exist"""
        with self.lock:
            value = self.tuples.pop(key, None)
            if value is None:
                return False, f"ERR {key}doesnotexist"
            return True, f"OK({key},{value})removed"

    def read(self, key):
        """Read key value pairs, return error if none exist"""
        with self.lock:
            value = self.tuples.get(key, None)
            if value is None:
                return False, f"ERR {key}doesnotexist"
            return True, f"OK({key},{value})read"







