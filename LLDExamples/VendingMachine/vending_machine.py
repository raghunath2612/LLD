from collections import defaultdict
from copy import copy
from typing import Dict, Optional
import threading
from abc import ABC, abstractmethod
from enum import  IntEnum

class Money(IntEnum):
    # Can add more denominations later.
    ONE = 1
    TWO = 2
    FIVE = 5
    TEN = 10
    TWENTY = 20
    FIFTY = 50


class Item:
    def __init__(self, name: str, code: str, price: int):
        self.name = name
        self.code = code
        self.price = price

class Inventory:
    def __init__(self):
        self.item_map: Dict[str, Item] = {}
        self.item_count: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()

    def get_item(self, item_code: str):
        if item_code not in self.item_map:
            return None
        return self.item_map[item_code]

    def add_item(self, item: Item, count: int):
        with self.lock:
            code = item.code
            self.item_map[code] = item
            self.item_count[code] = count

    def dispense_item(self, item_code):
        with self.lock:
            item = self.item_map[item_code]
            if self.item_count[item_code] <= 0:
                raise Exception("Item is out of stock")
            print(f"Dispensing item {item.name} from Rack: {item_code}")
            self.item_count[item_code] -= 1


    def check_if_item_available(self, item_code: str):
        with self.lock:
            if self.item_count[item_code] > 0:
                return True
            return False

class MoneyManager:
    def __init__(self):
        self.money_count: Dict[Money, int] = defaultdict(int)
        self._lock = threading.Lock()

    def add_money(self, money: Money, count: int):
        with self._lock:
            self.money_count[money] += count

    def check_change_available(self, money: int) -> bool:
        with self._lock:
            temp_money_count = copy(self.money_count)
            for denomination in sorted(Money, reverse=True):
                while money > 0 and  denomination <= money and temp_money_count[denomination] > 0:
                    money -= denomination
                    temp_money_count[denomination] -= 1
            if money == 0:
                return True
            return False

    def return_change(self, money: int):
        with self._lock:
            temp_money_count = copy(self.money_count)
            change = []
            for denomination in sorted(Money, reverse=True):
                while money > 0 and  denomination <= money and temp_money_count[denomination] > 0:
                    change.append(denomination)
                    money -= denomination
                    temp_money_count[denomination] -= 1
            if money == 0:
                self.money_count = temp_money_count
                return change
            raise Exception("Cannot return exact change.")


class VendingMachineState(ABC):
    def __init__(self, vending_machine: 'VendingMachine'):
        self.machine = vending_machine

    @abstractmethod
    def select_item(self, item_code: str):
        pass

    @abstractmethod
    def insert_money(self, money: Money):
        pass

    @abstractmethod
    def dispense_item(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

class IdleState(VendingMachineState):
    def select_item(self, item_code: str):
        item = self.machine.get_item(item_code)
        if not item:
            print("Given item code does not exist")
            return
        if not self.machine.is_item_available(item_code):
            print("Item is out of stock. Select another Item.")
            return
        self.machine.select_item_internal(item)
        self.machine.change_state(InsertMoneyState(self.machine))

    def insert_money(self, money: Money):
        print("Select item first")

    def dispense_item(self):
        print("Select Item first")

    def cancel(self):
        print("Select Item first")

class InsertMoneyState(VendingMachineState):
    def select_item(self, item_code: str):
        print("Item already selected. Cant select now. Cancel the transaction to select another item.")

    def insert_money(self, money: Money):
        self.machine.add_balance_internal(money)
        print(f"Added money: {money}, current balance: {self.machine.balance}")
        if self.machine.balance >= self.machine.selected_item.price:
            self.machine.change_state(EnoughMoneyState(self.machine))

    def dispense_item(self):
        print("Not Enough balance. Insert money.")

    def cancel(self):
        self.machine.cancel_internal()

class EnoughMoneyState(VendingMachineState):
    def select_item(self, item_code: str):
        print("Item already selected. Cant select now. Cancel the transaction to select another item.")

    def insert_money(self, money: Money):
        print("Enough money already inserted for the selected Item. No need to insert money.")

    def dispense_item(self):
        if not self.machine.selected_item:
            raise Exception("Item not selected.")
        item = self.machine.selected_item
        if self.machine.balance < item.price:
            raise Exception("Not enough balance inserted.")
        if not self.machine.check_change_available():
            print("Not Enough change available. Cannot Dispense Item")
            self.machine.cancel()
            return

        print(f"Dispensing Item: {item.name}")
        self.machine.dispense_item_internal()
        self.machine.set_idle_state()

    def cancel(self):
        self.machine.cancel_internal()



class VendingMachine:
    def __init__(self):
        self._balance: int = 0
        self._selected_item: Optional[Item] = None
        self._lock = threading.Lock()
        self._inventory: Inventory = Inventory()
        self._state: VendingMachineState = IdleState(self)
        self.money_manager: MoneyManager = MoneyManager()

    # Internal APIs


    def get_item(self, item_code):
        return self._inventory.get_item(item_code)

    def add_balance_internal(self, money: Money):
        with self._lock:
            self.money_manager.add_money(money, 1)
            self._balance += money

    def deduct_item_cost(self):
        with self._lock:
            if self._selected_item is None:
                print("Please select item first")
                return
            if self._selected_item.price > self._balance:
                print("Insert enough money.")
                return
            self._balance -= self._selected_item.price

    def set_idle_state(self):
        if self._balance > 0:
            self.refund_amount_internal()
        self._selected_item = None
        self.change_state(IdleState(self))

    def refund_amount_internal(self):
        with self._lock:
            if self._balance > 0:
                print(f"Refunding amount: {self.balance}")
                change = self.money_manager.return_change(self._balance)
                print(f"Change returned as: {change}")
                self._balance = 0

    def reset_selected_item(self):
        self._selected_item = None

    def add_money_internal(self, money: int):
        self._balance += money


    def dispense_item_internal(self):
        try:
            self.deduct_item_cost()
            self._inventory.dispense_item(self._selected_item.code)
            # self.refund_amount_internal()
        except Exception as e:
            self.add_money_internal(self._selected_item.price)
            self.cancel_internal()


    def cancel_internal(self):
        print("Cancelling transaction")
        self.set_idle_state()

    def check_change_available(self):
        if self.money_manager.check_change_available(self.balance - self._selected_item.price):
            return True
        return False

    @property
    def balance(self) -> int:
        return self._balance

    @property
    def selected_item(self) -> Optional[Item]:
        return self._selected_item

    def change_state(self, state: VendingMachineState):
        self._state = state

    def select_item_internal(self, item: Item):
        self._selected_item = item

    def is_item_available(self, item_code: str):
        return self._inventory.check_if_item_available(item_code)

    # External APIs
    def add_item(self, item_code: str, item_name: str, price: int, count: int):
        item = Item(item_name, item_code, price)
        self._inventory.add_item(item, count)

    def insert_money(self, money: Money):
        self._state.insert_money(money)

    def select_item(self, item_code: str):
        self._state.select_item(item_code)

    def dispense(self):
        self._state.dispense_item()

    def cancel(self):
        self._state.cancel()

if __name__ == "__main__":
    machine = VendingMachine()

    machine.add_item("A1", "Coke", 50, 1)
    machine.add_item("A2", "Pepsi", 50, 3)
    machine.add_item("B1", "Chips", 75, 10)

    print("=== Vending Machine Demo ===\n")

    print("Scenario 1: Buying Coke")
    machine.select_item("A1")
    machine.insert_money(Money.TEN)
    machine.insert_money(Money.TWENTY)
    machine.insert_money(Money.FIFTY)
    machine.dispense()

    print("\n---\n")

    print("Scenario 2: Insufficient funds")
    machine.select_item("B1")
    machine.insert_money(Money.TEN)
    machine.dispense()
    machine.insert_money(Money.FIFTY)
    machine.dispense()
    machine.insert_money(Money.TEN)
    machine.insert_money(Money.FIVE)
    machine.dispense()

    print("\n---\n")

    print("Scenario 3: Refund")
    machine.select_item("A2")
    machine.insert_money(Money.TWENTY)
    machine.cancel()

    print("\n---\n")

    print("Scenario 4: Out of stock")
    machine.select_item("A1")
    machine.insert_money(Money.TEN)
    machine.insert_money(Money.TWENTY)
    machine.insert_money(Money.FIFTY)
    machine.dispense()


"""
Design Patterns used.
1. Facade (VendingMachine class handles all the things the custoer needs instead of they calling the internal functions)
2. State pattern

Can be added.
3. SingleTon pattern. Only one vending machine instance. 
"""