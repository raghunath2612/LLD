import time
from abc import ABC, abstractmethod
from typing import Dict
from collections import deque
from enum import Enum
import threading

class RateLimitMessage(Enum):
    LIMIT_EXCEEDED = "Client used all Limits"
    APPROVED = "User can access requested Resource"

def get_precision_val(val: int):
    return int(val * 1000)

class RateLimitConfig:
    def __init__(self, capacity: int, time_frame_in_secs: int, token_refresh_rate: int):
        self.token_refresh_rate = token_refresh_rate
        self.window_size_in_secs = time_frame_in_secs
        self.capacity = capacity



class RequestResult:
    def __init__(self, is_success: bool, requests_remaining: int, message: RateLimitMessage, next_reset_time: int):
        self.next_reset_time = next_reset_time
        self.is_success = is_success
        self.requests_remaining = requests_remaining
        self.message  = message


class RateLimitStrategy(ABC):
    @abstractmethod
    def request(self, identifier: str, config: RateLimitConfig) -> RequestResult:
        pass

class WindowCounter:
    def __init__(self, window_size_in_secs: int):
        self.window_size_in_secs = window_size_in_secs * 1000
        self.window_start: int = int(time.time()) * 1000
        self.count = 0

    def increment_counter(self):
        self.count += 1

    def reset_counter(self):
        self.count = 0
        self.window_start = int(time.time()) * 1000

class FixedWindowStrategy(RateLimitStrategy):
    def __init__(self):
        self.counters: Dict[str, WindowCounter] = {}
        self._lock = threading.Lock()

    def request(self, identifier: str, config: RateLimitConfig) -> RequestResult:
        with self._lock:
            if identifier not in self.counters:
                counter = WindowCounter(get_precision_val(config.window_size_in_secs))
                self.counters[identifier] = counter

            counter = self.counters[identifier]
            if counter.window_start + counter.window_size_in_secs < get_precision_val(int(time.time())):
                counter.reset_counter()

            reset_time = counter.window_start + get_precision_val(int(time.time()))

            if counter.count >= config.capacity:
                return RequestResult(False, 0, RateLimitMessage.LIMIT_EXCEEDED,
                                     reset_time)

            counter.increment_counter()
            return RequestResult(True, config.capacity - counter.count,
                                 RateLimitMessage.APPROVED, reset_time)


class SlidingWindowStrategy(RateLimitStrategy):

    def __init__(self):
        self.requests: Dict[str, deque[int]] = {} # Contains create time of each request
        self._lock = threading.Lock()

    def request(self, identifier: str, config: RateLimitConfig) -> RequestResult:
        with self._lock:
            if identifier not in self.requests:
                self.requests[identifier] = deque()

            queue = self.requests[identifier]
            current_time = get_precision_val(int(time.time()))
            while queue and queue[0] + config.window_size_in_secs < current_time:
                queue.popleft()

            if len(queue) >= config.capacity:
                next_reset_time = queue[0] + get_precision_val(config.window_size_in_secs)
                return RequestResult(False, 0,
                                     RateLimitMessage.LIMIT_EXCEEDED, next_reset_time)

            queue.append(current_time)
            return RequestResult(True, config.capacity - len(queue),
                                 RateLimitMessage.APPROVED, current_time)


class TokenBucket:
    def __init__(self, capacity: int, token_refresh_rate: int):
        self.max_capacity = capacity
        self.tokens_left: int = capacity
        self.last_refill_time: int = get_precision_val(int(time.time()))
        self.token_refresh_rate: int = token_refresh_rate

    def has_token(self):
        return self.tokens_left > 0

    def consume_token(self):
        if self.tokens_left <= 0:
            raise Exception("Enough tokens not present")
        self.tokens_left -= 1

    def set_tokens(self, tokens: int):
        self.tokens_left = tokens

    def set_last_refill_time(self, time_val: int):
        self.last_refill_time = time_val

class TokenBucketStrategy(RateLimitStrategy):

    def __init__(self):
        self.requests: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def request(self, identifier: str, config: RateLimitConfig) -> RequestResult:
        with self._lock:
            if identifier not in self.requests[identifier]:
                self.requests[identifier] = TokenBucket(config.capacity, get_precision_val(config.token_refresh_rate))

            token_bucket = self.requests[identifier]

            current_time = get_precision_val(int(time.time()))
            newly_created_tokens = (current_time - token_bucket.last_refill_time) // token_bucket.token_refresh_rate

            if newly_created_tokens > 0:
                total_new_tokens = token_bucket.tokens_left + newly_created_tokens
                token_bucket.set_tokens(min(token_bucket.max_capacity, total_new_tokens))
                token_bucket.set_tokens(current_time)

            next_reset_time = token_bucket.last_refill_time + token_bucket.token_refresh_rate
            if token_bucket.tokens_left > 0:
                token_bucket.consume_token()
                return RequestResult(True, token_bucket.tokens_left, RateLimitMessage.APPROVED, next_reset_time)

            return RequestResult(False, 0, RateLimitMessage.LIMIT_EXCEEDED, next_reset_time)

"""
time.time() returns float value like this
232453223.121
First part is Second value from 1970.
Second part after . is nano second.

"""