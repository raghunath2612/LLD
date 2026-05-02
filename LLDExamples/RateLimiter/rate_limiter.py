from abc import ABC, abstractmethod
import threading
from typing import Dict
from enum import Enum
from collections import deque
from datetime import datetime, timedelta

def milliseconds(val: int):
    return val * 1000

class ResponseMessage(Enum):
    APPROVED = "Request Approved"
    LIMIT_EXCEEDED = "Limit Exceeded"

class RateLimiterConfig:
    def __init__(self, capacity: int, window_size: timedelta, refill_rate: timedelta):
        self.capacity = capacity
        self.window_size = window_size
        self.refill_rate = refill_rate


class RequestResult:
    def __init__(self, result: bool, requests_left: int, message: ResponseMessage, reset_time: datetime):
        self.result = result
        self.requests_left = requests_left
        self.message = message
        self.reset_time = reset_time



class RateLimiterStrategy(ABC):

    @abstractmethod
    def request(self, identifier: str, config: RateLimiterConfig):
        pass

class Counter:
    def __init__(self, window_size: timedelta, capacity: int):
        self.window_size = window_size
        self.capacity = capacity
        self.start_time: datetime = datetime.now()
        self.request_left = capacity

    def reset(self):
        self.start_time = datetime.now()
        self.request_left = self.capacity

    def consume_request(self):
        self.request_left -= 1

class FixedWindowStrategy(RateLimiterStrategy):
    def __init__(self):
        self.counters: Dict[str, Counter] = {}
        self._lock = threading.Lock()

    def request(self, identifier: str, config: RateLimiterConfig):
        with self._lock:
            current_time = datetime.now()
            if identifier not in self.counters:
                self.counters[identifier] = Counter(config.window_size, config.capacity)

            counter = self.counters[identifier]
            if current_time > counter.start_time + counter.window_size:
                counter.reset()

            reset_time = counter.start_time + counter.window_size
            if counter.request_left <= 0:
                return RequestResult(False, 0, ResponseMessage.LIMIT_EXCEEDED, reset_time)

            counter.consume_request()
            return RequestResult(True, counter.request_left, ResponseMessage.APPROVED, reset_time)

class SlidingWindowStrategy(RateLimiterStrategy):
    def __init__(self):
        self.requests: Dict[str, deque[datetime]] = {}
        self._lock = threading.Lock()

    def request(self, identifier: str, config: RateLimiterConfig):
        with self._lock:
            if identifier not in self.requests:
                self.requests[identifier] = deque()

            current_time = datetime.now()
            queue = self.requests[identifier]
            while queue and current_time >= queue[0] + config.window_size:
                queue.popleft()


            if len(queue) >= config.capacity:
                reset_time = queue[0] + config.window_size
                return RequestResult(False, 0, ResponseMessage.LIMIT_EXCEEDED, reset_time)

            queue.append(current_time)
            return RequestResult(True, config.capacity - len(queue), ResponseMessage.APPROVED, current_time + timedelta(seconds=1))

class TokenBucket:
    def __init__(self, capacity: int, last_refill_time: datetime, refill_rate: timedelta):
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill_time = last_refill_time
        self.refill_rate = refill_rate

    def refill_tokens(self):
        current_time = datetime.now()
        time_passed = (current_time - self.last_refill_time)
        new_tokens = time_passed // self.refill_rate

        if new_tokens > 0:
            self.tokens = min(new_tokens + self.tokens, self.capacity)
            self.last_refill_time = current_time

    def consume_token(self):
        if self.tokens == 0:
            raise Exception("No tokens left. Cannot consume")
        self.tokens -= 1


class TokenBucketStrategy(RateLimiterStrategy):
    def __init__(self):
        self.requests: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def request(self, identifier: str, config: RateLimiterConfig):
        with self._lock:
            current_time = datetime.now()
            if identifier not in self.requests:
                self.requests[identifier] = TokenBucket(config.capacity, current_time, config.refill_rate)

            token_bucket = self.requests[identifier]
            token_bucket.refill_tokens()

            reset_time = current_time + token_bucket.refill_rate
            if token_bucket.tokens == 0:
                return RequestResult(False, 0, ResponseMessage.LIMIT_EXCEEDED, reset_time)

            token_bucket.consume_token()
            return RequestResult(True, token_bucket.tokens, ResponseMessage.APPROVED, reset_time)


class RateLimiter:
    def __init__(self, rate_limiter_strategy: RateLimiterStrategy, capacity: int, window_size: timedelta,
                 refill_rate: timedelta,):
        self.rate_limiter_strategy = rate_limiter_strategy
        self.capacity = capacity
        self.window_size = window_size
        self.refill_rate = refill_rate

        self.config = RateLimiterConfig(capacity, window_size, refill_rate)

    def request(self, identifier: str):
        return self.rate_limiter_strategy.request(identifier, self.config)
