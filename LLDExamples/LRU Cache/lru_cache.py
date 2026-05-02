from typing import Optional, Dict
import threading

class Node:
    def __init__(self, key: int, val: int):
        self.key = key
        self.val = val
        self.next: Optional[Node] = None
        self.prev: Optional[Node] = None


class LRUCache:

    def __init__(self, cache_size: int):

        if cache_size <= 0:
            raise Exception("Cache size should be >= 1")
        self.cache_size = cache_size
        self.key_to_node: Dict[int, Node] = {}
        self.head: Node = Node(-1, -1)
        self.tail: Node = Node(-1, -1)
        self.head.next = self.tail
        self.tail.prev = self.head
        self._lock = threading.Lock()

    def insert_at_head(self, node: Node):
        temp = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = temp
        temp.prev = node
        self.key_to_node[node.key] = node

    def delete(self, node: Node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.next = None
        node.prev = None
        del self.key_to_node[node.key]

    def get(self, key: int):
        with self._lock:
            if key not in self.key_to_node:
                return -1
            node = self.key_to_node[key]
            self.delete(node)
            self.insert_at_head(node)
            return node.val

    def put(self, key: int, val: int):
        with self._lock:
            if key not in self.key_to_node and len(self.key_to_node) >= self.cache_size:
                self.delete(self.tail.prev)

            if key in self.key_to_node:
                node = self.key_to_node
                node.val = val
            else:
                node = Node(key, val)
            self.insert_at_head(node)




