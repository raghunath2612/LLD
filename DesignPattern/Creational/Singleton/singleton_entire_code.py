import threading
from threading import Lock

class SingleTon:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()

    def print_obj(self):
        print(self)

if __name__ == '__main__':
    obj1 = SingleTon.get_instance()
    obj2 = SingleTon.get_instance()
    obj1.print_obj()
    obj2.print_obj()
