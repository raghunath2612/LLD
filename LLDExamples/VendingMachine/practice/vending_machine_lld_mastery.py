"""
from enum import Enum
from abc import ABC, abstractmethod
from threading import Lock
from typing import Optional, Dict
from collections import defaultdict


class Coin(Enum):
    PENNY = 1
    NICKEL = 5
    DIME = 10
    QUARTER = 25

    def get_value(self) -> int:
        return self.value


class Inventory:
    def __init__(self):
        self.stock_map: Dict[str, int] = defaultdict(int)
        self.item_map: Dict[str, Item] = {}
        self.lock = Lock()

    def add_item(self, code: str, item: 'Item', qty: int):
        with self.lock:
            self.item_map[code] = item
            self.stock_map[code] = qty

    def get_item(self, code: str) -> Optional['Item']:
        return self.item_map.get(code)

    def is_available(self, code: str) -> bool:
        with self.lock:
            return self.stock_map.get(code, 0) > 0

    def reduce_stock(self, code: str) -> bool:
        with self.lock:
            if self.stock_map.get(code, 0) > 0:
                self.stock_map[code] -= 1
                return True
            return False

    def get_stock(self, code: str) -> int:
        with self.lock:
            return self.stock_map.get(code, 0)


class Item:
    def __init__(self, code: str, name: str, price: int):
        self.code = code
        self.name = name
        self.price = price

    def get_code(self) -> str:
        return self.code

    def get_name(self) -> str:
        return self.name

    def get_price(self) -> int:
        return self.price


class VendingMachineState(ABC):
    def __init__(self, machine):
        self.machine = machine

    @abstractmethod
    def select_item(self, code: str):
        pass

    @abstractmethod
    def insert_coin(self, coin: Coin):
        pass

    @abstractmethod
    def dispense(self):
        pass

    @abstractmethod
    def refund(self):
        pass


class DispensingState(VendingMachineState):
    def select_item(self, code: str):
        print("Transaction in progress. Please wait")

    def insert_coin(self, coin: Coin):
        print("Transaction in progress. Please wait")

    def dispense(self):
        print("Item already dispensed")

    def refund(self):
        print("Cannot refund after dispensing")


class HasMoneyState(VendingMachineState):
    def select_item(self, code: str):
        print("Item already selected. Please complete current transaction")

    def insert_coin(self, coin: Coin):
        self.machine.add_balance(coin.get_value())
        print(f"Inserted: {coin.name} (Balance: {self.machine.get_balance()} cents)")

    def dispense(self):
        selected_item = self.machine.get_selected_item()
        if not selected_item:
            print("No item selected")
            return

        item_price = selected_item.get_price()
        balance = self.machine.get_balance()

        if balance < item_price:
            print(f"Insufficient funds. Need {item_price - balance} more cents")
            return

        if not self.machine.get_inventory().is_available(selected_item.get_code()):
            print("Item is out of stock")
            self.machine.refund_balance()
            self.machine.set_state(IdleState(self.machine))
            return

        self.machine.set_state(DispensingState(self.machine))
        self.machine.dispense_item_internal()

    def refund(self):
        refund_amount = self.machine.get_balance()
        self.machine.refund_balance()
        self.machine.set_state(IdleState(self.machine))
        print(f"Refunded: {refund_amount} cents")


class IdleState(VendingMachineState):
    def select_item(self, code: str):
        if self.machine.get_inventory().is_available(code):
            self.machine.set_selected_item_code(code)
            self.machine.set_state(ItemSelectedState(self.machine))
            print(f"Item selected: {self.machine.get_selected_item().get_name()}")
        else:
            print(f"Item {code} is out of stock")

    def insert_coin(self, coin: Coin):
        print("Please select an item first")

    def dispense(self):
        print("Please select an item and insert money first")

    def refund(self):
        print("No money to refund")


class ItemSelectedState(VendingMachineState):
    def select_item(self, code: str):
        print("Item already selected. Please insert coins or cancel current selection")

    def insert_coin(self, coin: Coin):
        self.machine.add_balance(coin.get_value())
        print(f"Inserted: {coin.name} (Balance: {self.machine.get_balance()} cents)")

        selected_item = self.machine.get_selected_item()
        if selected_item and self.machine.get_balance() >= selected_item.get_price():
            self.machine.set_state(HasMoneyState(self.machine))

    def dispense(self):
        print("Please insert sufficient money first")

    def refund(self):
        refund_amount = self.machine.get_balance()
        self.machine.refund_balance()
        self.machine.set_state(IdleState(self.machine))
        print(f"Refunded: {refund_amount} cents")


class VendingMachine:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self.inventory = Inventory()
        self.balance = 0
        self.balance_lock = Lock()
        self.current_state: VendingMachineState = IdleState(self)
        self.selected_item_code: Optional[str] = None
        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()

    def select_item(self, code: str):
        self.current_state.select_item(code)

    def insert_coin(self, coin: Coin):
        self.current_state.insert_coin(coin)

    def dispense(self):
        self.current_state.dispense()

    def refund(self):
        self.current_state.refund()

    def dispense_item(self):
        item = self.get_selected_item()
        if not item:
            print("No item selected")
            return

        item_price = item.get_price()
        with self.balance_lock:
            current_balance = self.balance

        if current_balance < item_price:
            print("Insufficient funds")
            return

        if not self.inventory.reduce_stock(item.get_code()):
            print("Item is out of stock")
            self.refund_balance()
            self.set_state(IdleState(self))
            return

        print(f"Dispensing: {item.get_name()}")

        change = current_balance - item_price
        if change > 0:
            print(f"Returning change: {change} cents")

        with self.balance_lock:
            self.balance = 0

        self.selected_item_code = None
        self.set_state(IdleState(self))

    def reset(self):
        with self.balance_lock:
            self.balance = 0
        self.selected_item_code = None
        self.set_state(IdleState(self))

    def add_item(self, code: str, name: str, price: int, qty: int) -> Item:
        item = Item(code, name, price)
        self.inventory.add_item(code, item, qty)
        return item

    def get_selected_item(self) -> Optional[Item]:
        if not self.selected_item_code:
            return None
        return self.inventory.get_item(self.selected_item_code)

    def set_selected_item_code(self, code: str):
        self.selected_item_code = code

    def add_balance(self, amount: int):
        with self.balance_lock:
            self.balance += amount

    def refund_balance(self):
        with self.balance_lock:
            self.balance = 0

    def get_balance(self) -> int:
        with self.balance_lock:
            return self.balance

    def set_state(self, state: VendingMachineState):
        self.current_state = state

    def get_inventory(self) -> Inventory:
        return self.inventory


if __name__ == "__main__":
    machine = VendingMachine.get_instance()

    machine.add_item("A1", "Coke", 50, 5)
    machine.add_item("A2", "Pepsi", 50, 3)
    machine.add_item("B1", "Chips", 75, 10)

    print("=== Vending Machine Demo ===\n")

    print("Scenario 1: Buying Coke")
    machine.select_item("A1")
    machine.insert_coin(Coin.QUARTER)
    machine.insert_coin(Coin.QUARTER)
    machine.dispense()

    print("\n---\n")

    print("Scenario 2: Insufficient funds")
    machine.select_item("B1")
    machine.insert_coin(Coin.QUARTER)
    machine.dispense()

    print("\n---\n")

    print("Scenario 3: Refund")
    machine.select_item("A2")
    machine.insert_coin(Coin.QUARTER)
    machine.refund()

    print("\n---\n")

    print("Scenario 4: Out of stock")
    machine.select_item("A1")
    machine.insert_coin(Coin.QUARTER)
    machine.insert_coin(Coin.QUARTER)
    machine.dispense()
"""