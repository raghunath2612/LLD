import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import threading


def random_id() -> str:
    return str(uuid.uuid4())

class BookType(Enum):
    FICTIONAL = 'FICTIONAL'
    EDUCATIONAL = 'EDUCATIONAL'
    ACTION = 'ACTION'

class Role(Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'




class User:
    def __init__(self, name: str, age: int, address: str, ):
        # TODO: Add new class Address later
        self.address = address
        self.age = age
        self.name = name
        self.id = random_id()
        self.role: Role = Role.USER

    def __hash__(self):
        return self.id

class Librarian(User):
    def __init__(self, name: str, age: int, address: str,):
        super().__init__(name, age, address)
        self.role = Role.ADMIN

class Position:
    def __init__(self, floor: int, row: int, col: int):
        self.col = col
        self.row = row
        self.floor = floor

    def __str__(self):
        return f"Floor: {self.floor}, Row: {self.row}, Col: {self.col}"

class Rack:
    def __init__(self, position: Position):
        self.position = position

    def get_position(self) -> Position:
        return self.position


class Book:
    def __init__(self, title: str, author: str, book_type: BookType, isbn: str, publication_year: str):
        self.id = random_id()
        self.publication_year = publication_year
        self.isbn = isbn
        self.book_type = book_type
        self.author = author
        self.title = title

    def __hash__(self):
        return self.id

class BookItem:
    def __init__(self, book: Book, rack: Rack):
        self.book = book
        self.rack = rack
        self.user: Optional[User] = None

    def change_rack(self, rack: Rack):
        self.rack = rack

    def get_book_id(self) -> str:
        return self.book.id

    def add_booked_user(self, user: User):
        self.user = user

    def remove_user(self):
        self.user = None

class FineCalculatorStrategy(ABC):
    @abstractmethod
    def calculate_fine(self, delay_days: int) -> int:
        pass

class DefaultStrategy(FineCalculatorStrategy):
    pass

class NotificationObserver(ABC):
    @abstractmethod
    def notify_user(self, user: User, message: str):
        pass

class EmailNotification(NotificationObserver):
    pass

class SMSNotification(ABC):
    pass

class Reservation:
    def __init__(self, user: User, book: Book, days_for_expiry: int):
        self.user = user
        self.book = book
        self.created_time: datetime = datetime.now()
        self.expiry_date: Optional[datetime] = None

    def set_expiration_date(self, expiration_date: datetime):
        self.expiry_date = expiration_date

class Booking:
    def __init__(self, user: User, book_item: BookItem):
        self.id = random_id()
        self.user = user
        self.book_item = book_item
        self.time: datetime = datetime.now()
        self.is_active: bool = True

    def set_booking_inactive(self):
        self.is_active = False


class Fine:
    def __init__(self, user: User, amount: int, booking: Booking):
        self.user = user
        self.amount = amount
        self.booking = booking

class LibrarySystem:
    def __init__(self, reservation_expiration_days: int, free_booking_days: int, books_limit: int,
                 fine_calculator_strategy: FineCalculatorStrategy, maximum_allowed_fine: int,
                 observers: List[NotificationObserver]):
        self.free_booking_days = free_booking_days
        self.reservation_expiration_days = reservation_expiration_days
        self.books_limit = books_limit
        self.fine_calculator_strategy = fine_calculator_strategy
        self.maximum_allowed_fine = maximum_allowed_fine
        self.books: List[Book] = []
        self.book_items: Dict[str, List[BookItem]] = defaultdict(list)
        self.books_ordered_by_users: Dict[str, List[Booking]] = defaultdict(list) # key = User.id
        self.books_reservations: Dict[str, List[Reservation]] = defaultdict(list)  # key = Book.id
        self.created_reservations: Dict[str, List[Reservation]] = defaultdict(list) # Key = Book.id
        self.available_books: Dict[str, List[BookItem]] = defaultdict(list) # key = Book.id
        self.user_fines: Dict[str, List[Fine]] = defaultdict(list) # Key = User.id
        self._lock = threading.Lock()
        self.observers: List[NotificationObserver] = observers

    def add_book(self, book: Book):
        self.books.append(book)

    def add_book_item(self, book_item: BookItem):
        self.book_items[book_item.book.id].append(book_item)
        self.available_books[book_item.book.id].append(book_item)

    def find_book_location(self, book: 'Book') -> Optional[Position]:
        available_book_items = self.available_books[book.id]
        if available_book_items:
            return available_book_items[0].rack.get_position()
        return None

    def is_user_book_limit_exceeded(self, user: User):
        books_ordered_by_user = self.books_ordered_by_users[user.id]
        if len(books_ordered_by_user) >= self.books_limit:
            return True
        return False

    def calculate_fine_for_book_order(self, order: Booking):
        booked_time = order.time
        current_time = datetime.now()
        diff = current_time - booked_time
        if diff.days > self.free_booking_days:
            return self.fine_calculator_strategy.calculate_fine(diff.days)
        return 0

    def calculate_user_fine(self, user: User):
        returned_books_fine = sum(fine.amount for fine in self.user_fines[user.id])
        non_returned_books = self.books_ordered_by_users[user.id]
        non_returned_books_fine = sum(self.calculate_fine_for_book_order(order) for order in non_returned_books)
        return returned_books_fine + non_returned_books_fine

    def is_user_fine_exceeded(self, user: User):
        if self.calculate_user_fine(user) > self.maximum_allowed_fine:
            return False
        return True

    def order_book_item(self, user: User, book_item: BookItem) -> bool:
        with self._lock:
            if self.is_user_fine_exceeded(user):
                print("User current fine exceeded limit. Please pay fine before booking more books")
                return False
            if self.is_user_book_limit_exceeded(user):
                print("User currently holding more than expected limit of books. Please return books first.")
                return False

            if book_item not in self.available_books[book_item.get_book_id()]:
                print("Book is not present in the library")
                return False

            booking = Booking(user, book_item)
            self.books_ordered_by_users[user.id].append(booking)
            self.available_books[book_item.get_book_id()].remove(book_item)
            book_item.add_booked_user(user)
            return True

    def notify_book_availability(self, book: Book):
        if book.id in self.books_reservations:
            reservations = self.books_reservations[book.id]
            reservation = sorted(reservations, key=lambda x:x.created_date)[0]

            for observer in self.observers:
                observer.notify_user(reservation.user, f"{book.title} is available in Library.")
            reservation.set_expiration_date(datetime.now() + timedelta(days=self.reservation_expiration_days))
            reservations.remove(reservation)

    def return_book(self, user: User, book_item: BookItem) -> bool:
        with self._lock:
            if book_item.user != user:
                print("User didn't ordered this book")
                return False

            for booking in self.books_ordered_by_users[user.id]:
                if booking.book_item == book_item:
                    booking.set_booking_inactive()
                    book_item.user = None
                    self.available_books[book_item.get_book_id()].append(book_item)
                    self.notify_book_availability(book_item.book)

                    return True

            print("Book not available in user bookings")
            return False

    def reserve_book(self, book: Book, user: User) -> bool:
        with self._lock:
            book_location = self.find_book_location(book)
            if book_location:
                print(f"Book is already available at: {book_location}. No need to reserve.")
                return False

            reservation = Reservation(user, book, self.reservation_expiration_days)
            self.books_reservations[book.id].append(reservation)
            return True
