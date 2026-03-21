from collections import defaultdict
from typing import List, Set, Dict
from datetime import datetime, timedelta
import uuid
from abc import abstractmethod, ABC
import threading


def random_id():
    return str(uuid.uuid4())


class PricingStrategy(ABC):
    @abstractmethod
    def get_price(self) -> float:
        pass


class VIPPricingStrategy(PricingStrategy):
    def __init__(self, price: int):
        self.price = price

    def get_price(self) -> float:
        return self.price


class Seat:
    def __init__(self, seat_id: str, payment_strategy: PricingStrategy):
        self.seat_id = seat_id
        self.payment_strategy = payment_strategy

    def get_price(self):
        return self.payment_strategy.get_price()

    def __hash__(self):
        return hash(self.seat_id)

    def __eq__(self, other):
        return isinstance(other, Seat) and self.seat_id == other.seat_id


class Layout:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.seats: List[List[Seat | None]] = [[None for _ in range(cols)] for _ in range(rows)]

    def generate_seat_id(self, row: int, col: int):
        return f'{row}-{col}'

    def add_seat(self, row: int, col: int, payment_strategy: PricingStrategy) -> None:
        self.seats[row][col] = Seat(self.generate_seat_id(row, col), payment_strategy)

    def get_seat_by_position(self, row: int, col: int):
        return self.seats[row][col]

    def get_all_seats(self) -> List[List[Seat | None]]:
        return self.seats


class Ticket:
    def __init__(self, seat: Seat, time: datetime, price: float):
        self.seat = seat
        self.time = time
        self.price = price


class Order:
    def __init__(self, tickets: List[Ticket], order_date: datetime):
        self.tickets = tickets
        self.order_date = order_date

    def get_price(self) -> int:
        return sum(ticket.price for ticket in self.tickets)

    def get_all_tickets(self) -> List[Ticket]:
        return self.tickets


class Movie:
    def __init__(self, name: str, duration_in_mins: int, movie_id: int):
        self.name = name
        self.duration_in_mins = duration_in_mins
        self.movie_id = movie_id


class Screen:
    def __init__(self, layout: Layout, screen_id: int):
        self.layout = layout
        self.screen_id = screen_id

    def get_all_seats(self) -> List[List[Seat | None]]:
        return self.layout.get_all_seats()


class Screening:
    def __init__(self, movie: Movie, screen: Screen, start_time: datetime, end_time: datetime):
        self.id = random_id()
        self.screen = screen
        self.movie = movie
        self.start_time = start_time
        self.end_time = end_time

    @property
    def seats(self) -> List[List[Seat | None]]:
        return self.screen.get_all_seats()


class CinemaHall:
    def __init__(self, location: str):
        self.location = location
        self.screens: List[Screen] = []

    def add_screen(self, screen: Screen):
        self.screens.append(screen)


class MovieManager:
    def __init__(self):
        self.movies: List[Movie] = []

    def add_movie(self, movie: Movie):
        self.movies.append(movie)

    def delete_movie(self, movie: Movie):
        self.movies.remove(movie)

    def get_all_movies(self):
        return self.movies


class CinemaHallManager:
    def __init__(self):
        self.cinema_halls: List[CinemaHall] = []

    def add_cinema_hall(self, cinema_hall: CinemaHall):
        self.cinema_halls.append(cinema_hall)

    def add_screen_to_hall(self, cinema_hall: CinemaHall, screen: Screen):
        cinema_hall.add_screen(screen)


class SeatLock:
    def __init__(self, user_id: str, expiration_time: datetime):
        self.user_id = user_id
        self.expiration_time = expiration_time

    def is_expired(self):
        return self.expiration_time < datetime.now()


class SeatLockManager:
    def __init__(self, lock_duration: int):
        self.lock_duration = lock_duration
        self.locked_seats: Dict[str, SeatLock] = {}
        self.lock = threading.Lock()

    def generate_lock_id(self, seat: Seat, screening: Screening) -> str:
        return f"{screening.id}-{seat.seat_id}"

    def clean_lock_if_expired(self, lock_id: str):
        if lock_id in self.locked_seats:
            if self.locked_seats[lock_id].is_expired():
                del self.locked_seats[lock_id]

    def is_locked_by_user(self, seat: Seat, screening: Screening, user_id: str):
        lock_id = self.generate_lock_id(seat, screening)
        self.clean_lock_if_expired(lock_id)
        return lock_id in self.locked_seats and self.locked_seats[lock_id].user_id == user_id

    def is_lock_active(self, lock_id: str):
        self.clean_lock_if_expired(lock_id)
        return lock_id in self.locked_seats

    def lock_seat(self, seat: Seat, screening: Screening, user_id: str) -> bool:
        lock_id = self.generate_lock_id(seat, screening)
        with self.lock:
            if self.is_lock_active(lock_id):
                return False
            self.locked_seats[lock_id] = SeatLock(
                user_id,
                datetime.now() + timedelta(seconds=self.lock_duration)
            )
            return True

    def unlock_seat(self, seat: Seat, screening: Screening):
        lock_id = self.generate_lock_id(seat, screening)
        if lock_id in self.locked_seats:
            del self.locked_seats[lock_id]


class ScreeningManager:
    def __init__(self, seat_lock_manager: SeatLockManager):
        self.screenings_by_movie: Dict[Movie, List[Screening]] = defaultdict(list)
        self.tickets_by_screening: Dict[Screening, List[Ticket]] = defaultdict(list)
        self.booked_seats: Dict[Screening, Set[str]] = defaultdict(set)
        self.seat_lock_manager = seat_lock_manager

        # Per-seat locks
        self.seat_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)

    def _get_lock_key(self, screening: Screening, seat: Seat):
        return f"{screening.id}-{seat.seat_id}"

    def add_screening_to_movie(self, movie: Movie, screening: Screening):
        self.screenings_by_movie[movie].append(screening)

    def get_screening_by_movie(self, movie: Movie):
        return self.screenings_by_movie[movie]

    def book_tickets(self, screening: Screening, seats: List[Seat], user_id: str) -> Order:
        lock_keys = [self._get_lock_key(screening, seat) for seat in seats]
        lock_keys.sort()

        locks = [self.seat_locks[key] for key in lock_keys]

        acquired_locks = []

        # ✅ Non-blocking acquisition with rollback
        for lock in locks:
            if not lock.acquire(blocking=False):
                for l in acquired_locks:
                    l.release()
                raise Exception("One or more seats are being booked by another user")
            acquired_locks.append(lock)

        try:
            tickets = []

            for seat in seats:
                if seat.seat_id in self.booked_seats[screening]:
                    raise Exception(f"Seat {seat.seat_id} already booked")

                if not self.seat_lock_manager.is_locked_by_user(seat, screening, user_id):
                    raise Exception(f"Seat {seat.seat_id} not locked by user")

            for seat in seats:
                ticket = Ticket(seat, datetime.now(), seat.get_price())
                self.tickets_by_screening[screening].append(ticket)
                self.booked_seats[screening].add(seat.seat_id)
                self.seat_lock_manager.unlock_seat(seat, screening)
                tickets.append(ticket)

            return Order(tickets, datetime.now())

        finally:
            for lock in acquired_locks:
                lock.release()

    def get_available_seats(self, screening: Screening):
        available = []
        for row in screening.seats:
            for seat in row:
                if seat and seat.seat_id not in self.booked_seats[screening]:
                    available.append(seat)
        return available


class MovieTicketBookingSystem:
    def __init__(self):
        self.seat_lock_manager = SeatLockManager(lock_duration=300)
        self.screening_manager = ScreeningManager(self.seat_lock_manager)
        self.movie_manager = MovieManager()
        self.cinema_hall_manager = CinemaHallManager()

    def add_movie(self, movie: Movie):
        self.movie_manager.add_movie(movie)

    def get_all_movies(self):
        return self.movie_manager.get_all_movies()

    def add_screening_to_movie(self, movie: Movie, screening: Screening):
        self.screening_manager.add_screening_to_movie(movie, screening)

    def get_screening_by_movie(self, movie: Movie):
        return self.screening_manager.get_screening_by_movie(movie)

    def add_screen_to_cinema_hall(self, cinema_hall: CinemaHall, screen: Screen):
        self.cinema_hall_manager.add_screen_to_hall(cinema_hall, screen)

    def lock_seat(self, screening: Screening, seat: Seat, user_id: str):
        return self.seat_lock_manager.lock_seat(seat, screening, user_id)

    def book_ticket(self, screening: Screening, seats: List[Seat], user_id: str) -> Order:
        return self.screening_manager.book_tickets(screening, seats, user_id)

    def find_available_seats(self, screening: Screening):
        return self.screening_manager.get_available_seats(screening)