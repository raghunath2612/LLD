import random
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Optional, Dict


def generate_bank_account_id():
    #TODO: Change code to predefined
    id = random.randint(1000000, 999999)
    return str(id)


class DispenseChain(ABC):
    @abstractmethod
    def dispense(self, required_money: int):
        pass

    @abstractmethod
    def can_dispense(self, required_money: int) -> bool:
        pass

    @abstractmethod
    def set_next_chain(self, next_chain: 'DispenseChain'):
        pass

class NoteDispenser(DispenseChain):
    def __init__(self, value: int, notes_count: int):
        self.note_value = value
        self.notes_count = notes_count
        self.next_chain: Optional[DispenseChain] = None

    def dispense(self, required_money: int) -> None:
        if self.note_value <= required_money:
            notes_required = (required_money // self.note_value)
            required_money -= (notes_required * self.note_value)
            self.notes_count -= notes_required
            if required_money == 0:
                return
            if self.next_chain:
                return self.next_chain.dispense(required_money)
            raise Exception("Dont have required amount in the ATM")
        if self.next_chain:
            return self.next_chain.dispense(required_money)
        raise Exception("Dont have required amount in the ATM")



    def can_dispense(self, required_money: int) -> bool:
        if self.note_value <= required_money and self.notes_count > 0:
            notes_required = min(required_money // self.note_value, self.notes_count)
            required_money -= (notes_required * self.note_value)
            if required_money == 0:
                return True
            if self.next_chain:
                return self.next_chain.can_dispense(required_money)
            return False
        if self.next_chain:
            return self.next_chain.can_dispense(required_money)
        return False

    def set_next_chain(self, next_chain: DispenseChain):
        self.next_chain = next_chain


class CashDispenser:
    def __init__(self, hundreds: int, fifties: int, tens: int):
        note_dispenser_10 = NoteDispenser(10, tens)
        note_dispenser_50 = NoteDispenser(50, fifties)
        note_dispenser_100 = NoteDispenser(100, hundreds)

        note_dispenser_100.set_next_chain(note_dispenser_50)
        note_dispenser_50.set_next_chain(note_dispenser_10)
        self.chain = note_dispenser_100
        self._lock = threading.Lock()

    def can_dispense_cash(self, amount: int) -> bool:
        return self.chain.can_dispense(amount)

    def dispense(self, amount: int):
        with self._lock:
            if self.can_dispense_cash(amount):
                self.chain.dispense(amount)
            else:
                print("Cannot dispense exact amount.")

class AtmCard:
    def __init__(self, card_no: str, cvv: int, expiry_month: int, expiry_year: int):
        self.card_no = card_no
        self.cvv = cvv
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year

class BankAccount:
    def __init__(self, account_no: str, ifsc_code: str, balance: int = 0):
        self.account_no = account_no
        self.ifsc_code = ifsc_code
        self._balance = balance
        self._lock = threading.Lock()

    @property
    def balance(self):
        return self._balance

    def deduct_balance(self, amount: int):
        with self._lock:
            if self._balance < amount:
                raise Exception("Bank account does not have enough balance")
            self._balance -= amount

    def add_balance(self, amount: int):
        with self._lock:
            if amount < 0:
                raise Exception("Cannot add negative balance.")
            self._balance += amount

class BankSystem:
    def __init__(self):
        self.bank_accounts: Dict[str, BankAccount] = {}
        self.atm_to_bank: Dict[str, BankAccount] = {}
        self.atm_cards: Dict[str, AtmCard] = {}
        self.atm_pins: Dict[str, int] = {}
        self._account_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)

    def add_bank_account(self, account_no: str, ifsc_code: str, balance: int = 0):
        # TODO: For simplicity using predefined account_no. create account_no_generator to create account_no.
        bank_account = BankAccount(account_no, ifsc_code, balance)
        self.bank_accounts[account_no] = bank_account

    def add_atm(self, card_no: str, cvv: int, expiry_month: int, expiry_year: int, pin: int, account_no: str):
        # TODO: For simplicity using predefined card_no and pin. create id generator functions to create account_no and pin.
        atm = AtmCard(card_no, cvv, expiry_month, expiry_year)
        self.atm_cards[card_no] = atm
        self.atm_to_bank[card_no] = self.bank_accounts[account_no]
        self.atm_pins[card_no] = pin

    def is_valid_pin(self, card: AtmCard, pin: int) -> bool:
        return self.atm_pins[card.card_no] == pin

    def get_account_balance(self, card: AtmCard) -> int:
        bank_account = self.atm_to_bank[card.card_no]
        return bank_account.balance

    def has_enough_balance(self, card: AtmCard, amount: int) -> bool:
        bank_account = self.atm_to_bank[card.card_no]
        if bank_account.balance > amount:
            return True
        return False

    def deduct_balance_from_atm(self, card: AtmCard, amount: int):
        bank_account = self.atm_to_bank[card.card_no]
        if bank_account.balance < amount:
            raise Exception("Bank account does not have enough balance")
        bank_account.deduct_balance(amount)

    def add_balance(self, card: AtmCard, amount: int):
        bank_account = self.atm_to_bank[card.card_no]
        bank_account.add_balance(amount)


class ATMState(ABC):

    def __init__(self, atm_machine: 'ATMMachine'):
        self.atm_machine = atm_machine

    @abstractmethod
    def insert_card(self, card: AtmCard):
        pass

    @abstractmethod
    def enter_pin(self, pin: int):
        pass

    @abstractmethod
    def enquire_balance(self):
        pass

    @abstractmethod
    def deposit(self, amount: int):
        pass

    @abstractmethod
    def withdraw(self, amount: int):
        pass

    @abstractmethod
    def cancel(self):
        pass

class IdleState(ATMState):

    def insert_card(self, card: AtmCard):
        self.atm_machine.selected_card = card
        print("Card inserted successfully")
        self.atm_machine.set_state(CardInsertedState(self.atm_machine))

    def enter_pin(self, pin: int):
        print("Please insert ATM card first")

    def enquire_balance(self):
        print("Please insert ATM card first")

    def deposit(self, amount: int):
        print("Please insert ATM card first")

    def withdraw(self, amount: int):
        print("Please insert ATM card first")

    def cancel(self):
        pass

class CardInsertedState(ATMState):

    def insert_card(self, card: AtmCard):
        print("Card already inserted.")

    def enter_pin(self, pin: int):
        if self.atm_machine.is_valid_pin(pin):
            print("Card Authenticated successfully.")
            self.atm_machine.set_state(AuthenticatedState(self.atm_machine))
        else:
            print("Invalid Pin. Please enter again.")


    def enquire_balance(self):
        print("Please authenticate first by entering Pin.")

    def deposit(self, amount: int):
        print("Please authenticate first by entering Pin.")

    def withdraw(self, amount: int):
        print("Please authenticate first by entering Pin.")

    def cancel(self):
        self.atm_machine.cancel_internal()


class AuthenticatedState(ATMState):

    def insert_card(self, card: AtmCard):
        print("Card already inserted.")

    def enter_pin(self, pin: int):
        print("User already authenticated")

    def enquire_balance(self):
        balance = self.atm_machine.get_account_balance()
        print(f"Current balance = {balance}")

    def deposit(self, amount: int):
        self.atm_machine.deposit_internal(amount)

    def withdraw(self, amount: int):
        self.atm_machine.withdraw_internal(amount)

    def cancel(self):
        self.atm_machine.cancel_internal()


"""
Different states:
Idle, ATM Inserted, Authenticated, 
"""


class ATMMachine:
    def __init__(self, hundreds: int, fifties: int, tens: int, banking_system: BankSystem):
        self.selected_card: Optional[AtmCard] = None
        self.state: ATMState = IdleState(self)
        self.banking_system = banking_system
        self.cash_dispenser: CashDispenser = CashDispenser(hundreds, fifties, tens)

    # External Customer facing functions
    def insert_card(self, card: AtmCard):
        self.state.insert_card(card)

    def enter_pin(self, pin: int):
        self.state.enter_pin(pin)

    def enquire_balance(self):
        self.state.enquire_balance()

    def deposit(self, amount: int):
        self.state.deposit(amount)

    def withdraw(self, amount: int):
        self.state.withdraw(amount)

    def cancel(self):
        self.state.cancel()

    # Internal functions

    def withdraw_internal(self, amount: int):
        account_balance = self.get_account_balance()
        if account_balance < amount:
            print("Not enough money")
            return
        if not self.cash_dispenser.can_dispense_cash(amount):
            print("ATM does not have enough cash")
            return
        self.banking_system.deduct_balance_from_atm(self.selected_card, amount)
        self.cash_dispenser.dispense(amount)
        print("Cash dispensed from ATM.")

    def deposit_internal(self, amount: int):
        self.banking_system.add_balance(self.selected_card, amount)

    def cancel_internal(self):
        self.selected_card = None
        self.state = IdleState(self)
        print("Transaction cancelled.")

    def is_valid_pin(self, pin: int) -> bool:
        return self.banking_system.is_valid_pin(self.selected_card, pin)

    def set_state(self, state: ATMState):
        self.state = state

    def get_account_balance(self):
        return self.banking_system.get_account_balance(self.selected_card)






"""
Responsibilities:
ATM Card: Card no, cvv, expiry_mo, expiry_yr, pin
Bank Account: Account details, Balance
Bank System: Create an account, add ATM to account, validate ATM card,

ATM Machine: Insert card, enter pin, select type (Withdraw, deposit, Balance Enquiry) and go forward

"""