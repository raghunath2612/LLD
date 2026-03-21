import threading
import uuid
from collections import defaultdict
from typing import List, Dict, Set
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


def random_id() -> str:
    return str(uuid.uuid4())


# -------------------- MODELS --------------------

class Movie:
    def __init__(self, name: str, duration: int, genre: str):
        self.name = name
        self.duration = duration
        self.genre = genre


class PricingStrategy(ABC):
    @abstractmethod
    def get_price(self) -> float:
        pass


class VIPPricingStrategy(PricingStrategy):
    def __init__(self, price: float):
        self.price = price

    def get_price(self):
        return self.price


class Seat:
    def __init__(self, seat_id: str, pricing_strategy: PricingStrategy):
        self.seat_id = seat_id
        self.pricing_strategy = pricing_strategy

    def get_price(self):
        return self.pricing_strategy.get_price()

    def __hash__(self):
        return hash(self.seat_id)

    def __eq__(self, other):
        return isinstance(other, Seat) and self.seat_id == other.seat_id


class Layout:
    def __init__(self, rows: int, cols: int):
        self.seats = [[None for _ in range(cols)] for _ in range(rows)]

    def add_seat(self, row: int, col: int, strategy: PricingStrategy):
        self.seats[row][col] = Seat(f"{row}-{col}", strategy)

    def get_all_seats(self):
        return self.seats


class Screen:
    def __init__(self, screen_id: str, layout: Layout):
        self.screen_id = screen_id
        self.layout = layout


class Screening:
    def __init__(self, screen: Screen, movie: Movie, start: datetime, end: datetime):
        self.id = random_id()
        self.screen = screen
        self.movie = movie
        self.start = start
        self.end = end

        # Precompute seat set
        self.seat_set: Set[Seat] = set()
        for row in screen.layout.get_all_seats():
            for seat in row:
                if seat:
                    self.seat_set.add(seat)

    def __hash__(self):
        return hash(self.id)


class Ticket:
    def __init__(self, screening: Screening, seat: Seat):
        self.screening = screening
        self.seat = seat

    def __hash__(self):
        return hash((self.screening.id, self.seat.seat_id))


class Order:
    def __init__(self, tickets: List[Ticket], user: 'User'):
        self.tickets = tickets
        self.user = user
        self.time = datetime.now()

    def calculate_price(self):
        return sum(t.seat.get_price() for t in self.tickets)


class User:
    def __init__(self, name: str):
        self.id = random_id()
        self.name = name


# -------------------- LOCKING --------------------

class SeatLock:
    def __init__(self, user: User, expiry: datetime):
        self.user = user
        self.expiry = expiry

    def is_expired(self):
        return datetime.now() > self.expiry


class SeatLockManager:
    def __init__(self, duration_sec: int):
        self.duration = duration_sec
        self.seat_locks: Dict[str, SeatLock] = {}
        self.locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)

    def _id(self, screening: Screening, seat: Seat):
        return f"{screening.id}-{seat.seat_id}"

    def lock_seat(self, screening: Screening, seat: Seat, user: User) -> bool:
        lock_id = self._id(screening, seat)
        mutex = self.locks[lock_id]

        with mutex:
            if lock_id in self.seat_locks:
                lock = self.seat_locks[lock_id]
                if not lock.is_expired():
                    return False

            self.seat_locks[lock_id] = SeatLock(
                user,
                datetime.now() + timedelta(seconds=self.duration)
            )
            return True

    def validate_lock(self, screening: Screening, seat: Seat, user: User) -> bool:
        lock_id = self._id(screening, seat)
        mutex = self.locks[lock_id]

        with mutex:
            if lock_id not in self.seat_locks:
                return False

            lock = self.seat_locks[lock_id]
            if lock.is_expired():
                del self.seat_locks[lock_id]
                return False

            return lock.user == user

    def unlock(self, screening: Screening, seat: Seat):
        lock_id = self._id(screening, seat)
        mutex = self.locks[lock_id]

        with mutex:
            if lock_id in self.seat_locks:
                del self.seat_locks[lock_id]


# -------------------- BOOKING --------------------

class ScreeningManager:
    def __init__(self, lock_duration: int):
        self.booked: Dict[Screening, Set[Seat]] = defaultdict(set)
        self.lock_manager = SeatLockManager(lock_duration)

    def book_tickets(self, seats: List[Seat], screening: Screening, user: User) -> Order:
        # Validate seats
        for seat in seats:
            if seat not in screening.seat_set:
                raise Exception("Invalid seat")

        # Sort locks (deadlock prevention)
        lock_ids = [self.lock_manager._id(screening, s) for s in seats]
        lock_ids.sort()

        locks = [self.lock_manager.locks[lid] for lid in lock_ids]

        acquired = []
        try:
            for lock in locks:
                if not lock.acquire(blocking=False):
                    raise Exception("Concurrent booking conflict")
                acquired.append(lock)

            # Validation
            for seat in seats:
                if seat in self.booked[screening]:
                    raise Exception("Already booked")

                if not self.lock_manager.validate_lock(screening, seat, user):
                    raise Exception("Seat not locked by user")

            # Commit
            tickets = []
            for seat in seats:
                self.booked[screening].add(seat)
                self.lock_manager.unlock(screening, seat)
                tickets.append(Ticket(screening, seat))

            return Order(tickets, user)

        finally:
            for lock in acquired:
                lock.release()