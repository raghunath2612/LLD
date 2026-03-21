import threading
import uuid
from collections import defaultdict
from typing import List, Dict, Set
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


def random_id() -> str:
    return str(uuid.uuid4())

class Movie:
    def __init__(self, movie_name: str, duration_in_mins, genre: str):
        self.movie_name = movie_name
        self.duration_in_mins = duration_in_mins
        self.genre = genre

    def get_duration_in_mins(self):
        return self.duration_in_mins

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

    def get_price(self):
        return self.pricing_strategy.get_price()

class Layout:
    def __init__(self, rows: int, cols: int):
        self.seats: List[List[Seat | None]] = [[None for i in range(cols)] for j in range(rows)]

    def generate_seat_id(self, row, col) -> str:
        return f"{row}-{col}"

    def add_seat(self, row: int, col: int, pricing_strategy: PricingStrategy) -> None:
        self.seats[row][col] = Seat(self.generate_seat_id(row, col), pricing_strategy)

    def get_all_seats(self) -> List[List[Seat]]:
        return self.seats

class Screen:
    def __init__(self, screen_id: str, layout: Layout):
        self.screen_id = screen_id
        self.layout = layout

    def generate_seat_id(self, row, col) -> str:
        return f"{row}-{col}"


    def get_all_seats(self) -> List[List[Seat]]:
        return self.layout.seats


class MovieHall:
    def __init__(self, hall_name: str, screens: List[Screen]):
        self.hall_name = hall_name
        self.screens = screens

    def add_screen(self, screen: Screen) -> None:
        self.screens.append(screen)



class Screening:
    def __init__(self, screen: Screen, movie: Movie, start_time:datetime, end_time: datetime):
        self.id = random_id()
        self.screen = screen
        self.movie = movie
        self.start_time = start_time
        self.end_time = end_time

    def get_duration_in_mins(self):
        return self.movie.get_duration_in_mins()

    @property
    def seats(self) -> List[List[Seat]]:
        return self.screen.get_all_seats()

    @property
    def all_seats(self) -> List[Seat]:
        seats = []
        for row in self.seats:
            for seat in row:
                seats.append(seat)
        return seats

    def __hash__(self):
        return hash(self.id)

class Ticket:
    def __init__(self, screening: Screening, seat: Seat):
        self.screening = screening
        self.seat = seat

class Order:
    def __init__(self, tickets: List[Ticket], time: datetime, user: 'User'):
        self.tickets = tickets
        self.time = time
        self.user = user

    def calculate_price(self):
        price = 0
        for ticket in self.tickets:
            price += ticket.seat.get_price()
        return price

class User:
    def __init__(self, user_name: str):
        self.id = random_id()
        self.user_name = user_name
        # Add booking per user later

    def __hash__(self):
        return hash(self.id)

class SeatLock:
    def __init__(self, user: User, expiration_time: datetime):
        self.user = user
        self.expiration_time = expiration_time

    def is_lock_expired(self) -> bool:
        if datetime.now() > self.expiration_time:
            return True
        return False

class SeatLockManager:
    def __init__(self, lock_duration_in_seconds: int):
        self.lock_duration = lock_duration_in_seconds
        self.seat_locks: Dict[str, SeatLock] = {}
        self.locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)

    def generate_lock_id(self, screening: Screening, seat: Seat):
        return f"{screening.id}-{seat.seat_id}"

    def is_lock_active(self, seat: Seat, screening: Screening):
        lock_id = self.generate_lock_id(screening, seat)
        if lock_id not in self.seat_locks:
            return False
        lock = self.seat_locks[lock_id]
        if lock.is_lock_expired():
            del self.seat_locks[lock_id]
            return False
        return True


    def check_if_locked_by_user(self, screening: Screening, seat: Seat, user: User) -> bool:
        lock_id = self.generate_lock_id(screening, seat)
        with self.locks[lock_id]:
            if lock_id not in self.seat_locks:
                return False
            lock = self.seat_locks[lock_id]
            return self.is_lock_active(seat, screening) and lock.user is user

    def lock_seat(self, screening: Screening, seat: Seat, user: User) -> bool:
        lock_id = self.generate_lock_id(screening, seat)
        with self.locks[lock_id]:
            if self.is_lock_active(seat, screening):
                return False
            lock = SeatLock(user, datetime.now() + timedelta(seconds=self.lock_duration))
            self.seat_locks[lock_id] = lock
            return True

    def unlock_seat(self, screening: Screening, seat: Seat):
        lock_id = self.generate_lock_id(screening, seat)
        with self.locks[lock_id]:
            if lock_id in self.seat_locks:
                del self.seat_locks[lock_id]


class ScreeningManager:
    def __init__(self, lock_duration: int):
        self.tickets_by_screening: Dict[Screening, Set[Ticket]] = defaultdict(set)
        self.screens_by_movie: Dict[Movie, List[Screening]] = defaultdict(list)
        self.booked_tickets: Dict[Screening, Set[Seat]] = defaultdict(set)
        self.seat_lock_manager: SeatLockManager = SeatLockManager(lock_duration)

    def generate_lock_id(self, seat: Seat, screening: Screening):
        return self.seat_lock_manager.generate_lock_id(screening, seat)

    def check_if_seats_are_part_of_screening(self, seats: List[Seat], screening: Screening):
        for seat in seats:
            if seat not in screening.all_seats:
                return False
        return True

    def book_tickets(self, seats: List[Seat], screening: Screening, user: User) -> Order:
        if not self.check_if_seats_are_part_of_screening(seats, screening):
            raise Exception("Seats are not part of Screening")
        lock_ids: List[str] = [self.generate_lock_id(seat, screening) for seat in seats]
        lock_ids.sort() # For avoiding dead locks
        locks: List[threading.Lock] = [self.seat_lock_manager.locks[lock_id] for lock_id in lock_ids]
        acquired_locks: List[threading.Lock] = []
        try:

            for lock in locks:
                if not lock.acquire(blocking=False):
                    raise Exception("Seat already locked by other user")
                acquired_locks.append(lock)

            tickets: List[Ticket] = []
            for seat in seats:
                if seat in self.booked_tickets[screening]:
                    raise Exception("Ticket already booked")

                if not self.seat_lock_manager.check_if_locked_by_user(screening, seat, user):
                    raise Exception("Seat not locked by current user. Need to lock before booking.")

            for seat in seats:
                ticket = Ticket(screening, seat)
                tickets.append(ticket)
                self.tickets_by_screening[screening].add(ticket)
                self.booked_tickets[screening].add(ticket.seat)

            order = Order(tickets, datetime.now(), user)
            return order
        finally:
            for lock in acquired_locks:
                lock.release()

    # Add code similarly for adding screens.
    def get_movie_by_screen(self, movie: Movie) -> List[Screening]:
        return self.screens_by_movie[movie]


# Create managers for CinemaHall to add and delete movies, Movie to add and delete movies,
"""
Reason for having 2 level locks. One in ScreeningManager, Another in SeatLockManager.
SeatLockManager:
    Firstly the client will try to lock the seats by selecting in the UI one by one.
    Once the seats are selected they will be present in the SeatLockManager.seat_locks (This contains who locked what). 
            -> This is used for concurrency at the database level.
    But, for the process where we dont want multiple processes to run the same piece of code which assigns lock on same resource we use threading.Lock().
            -> It is present with lock: in both ScreeningManager and SeatLockManager.

"""