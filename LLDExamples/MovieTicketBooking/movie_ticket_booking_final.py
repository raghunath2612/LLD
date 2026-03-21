"""
Flow
Seat -> Layout -> Screen -> Screening
CinemaHall
Movie
ScreeningManager
SeatLock
SeatLockManager
MovieManager
CinemaHalManager
"""
import threading
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Dict, Set
from datetime import datetime, timedelta


def random_id() -> str:
    return str(uuid.uuid4())

class PricingStrategy(ABC):
    @abstractmethod
    def get_price(self) -> float:
        pass

class VIPPricingStrategy(PricingStrategy):
    def __init__(self, price: float):
        self.price = price

    def get_price(self) -> float:
        return self.price

class Seat:
    def __init__(self, seat_id: str, pricing_strategy: PricingStrategy):
        self.seat_id = seat_id
        self.pricing_strategy = pricing_strategy

    def get_price(self) -> float:
        return self.pricing_strategy.get_price()

    def __hash__(self):
        return hash(self.seat_id)

class Movie:
    def __init__(self, title: str, duration_in_mins: int, movie_id: int):
        self.id = movie_id
        self.title = title
        self.duration_in_mins = duration_in_mins


class Layout:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.seats: List[List[Seat | None]] = [[None for _ in range(cols)] for _ in range(rows)]

    def add_seat(self, row: int, col: int, pricing_strategy: PricingStrategy):
        self.seats[row][col] = Seat(random_id(), pricing_strategy)

    def get_seats(self) -> List[List[Seat | None]]:
        return self.seats

class Screen:
    def __init__(self, layout:Layout):
        self.layout = layout

    def get_seats(self) -> List[List[Seat | None]]:
        return self.layout.seats

class CinemaHall:
    def __init__(self, screens: List[Screen], location: str, title: str):
        self.screens = screens
        self.location = location
        self.title = title

    def add_screen(self, screen: Screen) -> None:
        self.screens.append(screen)


class Screening:
    def __init__(self, screen: Screen, movie: Movie, start_time: datetime, end_time, screening_id: int):
        self.screen = screen
        self.movie = movie
        self.start_time = start_time
        self.end_time = end_time
        self.id = screening_id
        self.seats = []
        for row in self.screen.get_seats():
            for seat in row:
                self.seats.append(seat)

    def __hash__(self):
        return hash(self.id)

class Ticket:
    def __init__(self, ticket_id: str, seat: Seat, screening: Screening):
        self.id = ticket_id
        self.seat = seat
        self.screening = screening

    def get_ticket_cost(self) -> float:
        return self.seat.get_price()

class User:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.orders: List[Order] = []
        # TODO Add code to track booking done by user

    def add_order(self, order: 'Order'):
        self.orders.append(order)

class Order:
    def __init__(self, tickets: List[Ticket], order_time: datetime, user: User):
        self.tickets = tickets
        self.order_time = order_time
        self.user = user

    def get_order_total_cost(self) -> float:
        cost = 0
        for ticket in self.tickets:
            cost += ticket.get_ticket_cost()
        return cost

class SeatLock:
    def __init__(self, user: User, expiration_time: datetime):
        self.user = user
        self.expiration_time = expiration_time

    def is_lock_expired(self):
        if self.expiration_time > datetime.now():
            return False
        return True

class SeatLockManager:
    def __init__(self, lock_duration_in_seconds: int):
        self.lock_duration = lock_duration_in_seconds
        self.seat_locks: Dict[str, SeatLock] = {}
        self.mutex_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)

    def generate_lock_id(self, seat: Seat, screening: Screening) -> str:
        return f"{seat.seat_id}-{screening.id}"

    def check_if_lock_exists(self, seat: Seat, screening: Screening):
        lock_id = self.generate_lock_id(seat, screening)
        if lock_id not in self.seat_locks:
            return False
        seat_lock = self.seat_locks[lock_id]
        if seat_lock.is_lock_expired():
            del self.seat_locks[lock_id]
            return False
        return True

    def lock_seat(self, seat: Seat, screening: Screening, user: User) -> bool:
        lock_id = self.generate_lock_id(seat, screening)
        mutex = self.mutex_locks[lock_id]
        with mutex:
            if self.check_if_lock_exists(seat, screening):
                return False
            lock = SeatLock(user, datetime.now() + timedelta(seconds=self.lock_duration))
            self.seat_locks[lock_id] = lock
            return True

    def is_locked_by_user(self, seat: Seat, screening: Screening, user: User):
        lock_id = self.generate_lock_id(seat, screening)
        mutex = self.mutex_locks[lock_id]
        with mutex:
            if not self.check_if_lock_exists(seat, screening):
                return False
            lock = self.seat_locks[lock_id]
            return lock.user.user_id == user.user_id

    def remove_lock(self, seat: Seat, screening: Screening):
        lock_id = self.generate_lock_id(seat, screening)
        mutex = self.mutex_locks[lock_id]
        with mutex:
            if self.check_if_lock_exists(seat, screening):
                del self.seat_locks[lock_id]

class ScreeningManager:
    def __init__(self, seat_lock_duration_in_sec: int):
        self.movies_by_location: Dict[str, List[Movie]] = defaultdict(list)
        self.tickets_by_screening: Dict[Screening, List[Ticket]]= defaultdict(list)
        self.booked_tickets: Dict[Screening, Set[Seat]] = defaultdict(set)
        self.seat_lock_manager = SeatLockManager(seat_lock_duration_in_sec)

    @property
    def mutex_locks(self) -> Dict[str, threading.Lock]:
        return self.seat_lock_manager.mutex_locks

    def check_if_seats_are_part_of_screening(self, seats: List[Seat], screening: Screening) -> bool:
        for seat in seats:
            if seat not in screening.seats:
                return False
        return True

    def generate_lock_id(self, seat: Seat, screening: Screening) -> str:
        return self.seat_lock_manager.generate_lock_id(seat, screening)

    def book_tickets(self, seats: List[Seat], screening: Screening, user: User):
        if not self.check_if_seats_are_part_of_screening(seats, screening):
            raise Exception("Seats are not part of Screening")

        lock_ids: List[str] = [self.generate_lock_id(seat, screening) for seat in seats]
        lock_ids.sort() # To avoid deadlocks

        locks: List[threading.Lock] = [self.mutex_locks[lock_id] for lock_id in lock_ids]

        acquired_locks: List[threading.Lock] = []
        try:
            for lock in locks:
                if not lock.acquire(blocking=False):
                    raise Exception("Other process has locked these seats")
                acquired_locks.append(lock)

            for seat in seats:
                if seat in self.booked_tickets[screening]:
                    raise Exception("Ticket already booked by someone")

                if not self.seat_lock_manager.is_locked_by_user(seat, screening, user):
                    raise Exception("Seat not locked by user. First user should lock the seat ant then book.")

            tickets = []
            for seat in seats:
                ticket = Ticket(random_id(), seat, screening)
                tickets.append(ticket)
                self.tickets_by_screening[screening].append(ticket)
                self.booked_tickets[screening].add(seat)

            order = Order(tickets, datetime.now(), user)
            user.add_order(order)
            return order
        finally:
            for lock in acquired_locks:
                lock.release()

# TODO: Add MovieManager and CinemaHall Manager to manage Movies and CinemaHall

"""
mutex (short for mutual exclusion) is a synchronization primitive used in programming to prevent multiple threads
    or processes from accessing a shared resource simultaneously.
It acts as a lock, ensuring only one thread can access a critical section of code at a time to prevent
    data corruption and race conditions.
"""