import threading

class TupleSpace:
    def __init__(self):
        self.tuples = {}
        self.lock = threading.Lock()

    def put(self, key, value):
        with self.lock:
            if key in self.tuples:
                return False, f"ERR {key} already exists"
            self.tuples[key] = value
            return True, f"OK({key},{value}) added"

    def get(self, key):
        with self.lock:
            value = self.tuples.pop(key, None)
            if value is None:
                return False, f"ERR {key} does not exist"
            return True, f"OK({key},{value}) removed"

    def read(self, key):
        with self.lock:
            value = self.tuples.get(key, None)
            if value is None:
                return False, f"ERR {key} does not exist"
            return True, f"OK({key},{value}) read"








