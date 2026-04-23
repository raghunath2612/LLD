from collections import defaultdict
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime, timedelta
import threading
from abc import ABC, abstractmethod

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

class BookStatus(Enum):
    AVAILABLE = 'AVAILABLE'
    RESERVED = 'RESERVED'
    BOOKED = 'BOOKED'

class Category(Enum):
    FICTION = 'FICTION'
    EDUCATIONAL = 'EDUCATIONAL'
    DRAMA = 'DRAMA'

class Order:
    def __init__(self, member: 'Member', book_item: 'BookItem'):
        self.member = member
        self.order_date = datetime.now()
        self.book_item = book_item

class Fine:
    def __init__(self, order: Order, amount: int):
        self.order = order
        self.amount = amount

class NotificationObserver(ABC):
    @abstractmethod
    def send_notification(self, member: 'Member', message: str):
        pass

class EmailNotificationService(NotificationObserver):
    def send_notification(self, member: 'Member', message: str):
        print(f"Sent mail to {member.email}")

class SMSNotificationService(NotificationObserver):
    def send_notification(self, member: 'Member', message: str):
        print(f"Sent message to {member.mobile_no}")


class FineCalculatorStrategy(ABC):
    @abstractmethod
    def calculate_fine(self, book_item: 'BookItem') -> Optional[Fine]:
        pass

    
class Member:
    def __init__(self, name: str, address: str, max_fine_allowed: int, max_books_allowed: int,
                 free_days: int, fine_calculator_strategy: FineCalculatorStrategy,
                 notification_observers: List[NotificationObserver],
                 email: str, mobile_no: str):
        self.mobile_no = mobile_no
        self.email = email
        self.notification_observers = notification_observers
        self.fine_calculator_strategy = fine_calculator_strategy
        self.free_days = free_days
        self.max_books_allowed = max_books_allowed
        self.max_fine_allowed = max_fine_allowed
        self.address = address
        self.name = name
        self.ordered_books: Dict[str, BookItem] = {}
        self.fines: List[Fine] = []
        self._lock = threading.Lock()

    def can_assign_book(self) -> bool:
        if len(self.ordered_books) >= self.max_books_allowed:
            print("User already took max limit books")
            return False
        returned_books_fine = sum(fine.amount for fine in self.fines)

        un_returned_books_fine = sum(self.fine_calculator_strategy.calculate_fine(self.ordered_books[book]) for book in self.ordered_books)
        if returned_books_fine + un_returned_books_fine > self.max_fine_allowed:
            print("User fine has crossed fine threshold")
            return False
        return True


    def assign_book(self, book_item: 'BookItem'):
        with self._lock:
            if not self.can_assign_book():
                raise Exception("User already assigned max limit books")
            self.ordered_books[book_item.barcode] = book_item
            book_item.set_assign_date(datetime.now())
            book_item.set_due_date(datetime.now() + timedelta(days=self.free_days))
            book_item.set_assigned_member(self)
            book_item.set_status(BookStatus.BOOKED)

    def return_book(self, book_item: 'BookItem') -> bool:
        with self._lock:
            if book_item.barcode not in self.ordered_books:
                print("User is not assigned with the book")
                return False

            fine = self.fine_calculator_strategy.calculate_fine(book_item)
            if fine:
                self.fines.append(fine)
            reservation = book_item.get_book().get_first_reservation()
            book_item.set_assigned_member(None)
            book_item.set_status(BookStatus.AVAILABLE)
            if reservation:
                book_item.set_reservation(reservation)
                book_item.set_status(BookStatus.RESERVED)
                for observer in self.notification_observers:
                    observer.send_notification(reservation.member, f"Book {book_item.get_book().get_title()} is available")

            return True



class Reservation:
    def __init__(self, member: Member, book: 'Book', expiry_date: datetime):
        self.expiry_date = expiry_date
        self.book = book
        self.member = member

    def get_expiry_date(self) -> datetime:
        return self.expiry_date



class BookItem:
    def __init__(self, book_status: BookStatus, rack: Rack, barcode: str, book: 'Book'):
        self.barcode = barcode
        self.status = book_status
        self.rack = rack
        self.assign_date: Optional[datetime] = None
        self.due_date: Optional[datetime] = None
        self.assigned_member: Optional[Member] = None
        self.reservation: Optional[Reservation] = None
        self.book: Book = book

    def set_assign_date(self, date: datetime):
        self.assign_date = date

    def set_due_date(self, date: datetime):
        self.due_date = date

    def set_assigned_member(self, member: Optional[Member]):
        self.assigned_member = member

    def set_status(self, status: BookStatus):
        self.status = status

    def set_reservation(self, reservation: Reservation):
        self.reservation = reservation

    def assign_book_to_member(self, member: Member) -> bool:
        try:
            if member.can_assign_book():
                member.assign_book(self)
                return True
        except Exception as e:
            return False
        return False

    def get_book(self) -> 'Book':
        return self.book


class Book:
    def __init__(self, title: str, author: str, category: Category, isbn: str, published_year: int):
        self.published_year = published_year
        self.isbn = isbn
        self.category = category
        self.author = author
        self.title = title
        self.book_items: List[BookItem] = []
        self.reservations: List[Reservation] = []

    def add_book_item(self, book_item: BookItem):
        self.book_items.append(book_item)

    def remove_book_item(self, book_item: BookItem):
        self.book_items.remove(book_item)

    def get_title(self) -> str:
        return self.title

    def get_available_books(self) -> List[BookItem]:
        return [book_item for book_item in self.book_items if book_item.status == BookStatus.AVAILABLE]

    def get_first_reservation(self) -> Optional[Reservation]:
        reservations = sorted(self.reservations, key= lambda reservation: reservation.expiry_date)
        if reservations:
            return reservations[0]
        return None

    def remove_reservations(self):
        for book_item in self.book_items:
            if book_item.reservation.get_expiry_date() > datetime.now():
                book_item.set_status(BookStatus.AVAILABLE)

class Library:
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
        self.books: Dict[str, Book] = {} # key = Book.isbn
        self._initialized = True
        self.notification_observers: List[NotificationObserver] = []


    def add_book(self, book: Book):
        self.books[book.isbn] = book

    def add_book_item(self, book: Book, rack: Rack, barcode: str):
        book_item = BookItem(BookStatus.AVAILABLE, rack, barcode, book)
        book = book_item.get_book()
        self.books[book.isbn].book_items.append(book_item)

    @classmethod
    def get_instance(cls):
        return cls()

    def add_observer(self, observer: NotificationObserver):
        self.notification_observers.append(observer)

    def create_book(self, title: str, author: str, isbn: str, category: Category, published_year):
        book = Book(title, author, category, isbn, published_year)
        self.books[isbn] = book

# Not completed total. But enough.
