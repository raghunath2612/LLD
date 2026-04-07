from collections import defaultdict
from typing import Dict, Optional
from uuid import uuid4
from abc import ABC
from enum import IntEnum
import threading

def random_id():
    return str(uuid4())

class Money(IntEnum):
    # Add more formats later
    ONE = 1
    TWO = 2
    FIVE = 5
    TEN = 10
    TWENTY = 20
    FIFTY = 50


class Item:
    def __init__(self, name: str, item_code: str, cost: float):
        self.name = name
        self.cost = cost
        self.item_code = item_code


class Inventory:
    def __init__(self):
        self.item_map: Dict[str, Item] = {}
        self.item_count: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()

    def add_item(self, item_name: str, cost: float, count: int, item_code: str):
        item = Item(item_name, item_code, cost)
        with self.lock:
            self.add_item_object(item, count)

    def add_item_object(self, item: Item, count: int):
        with self.lock:
            self.item_map[item.item_code] = item
            self.item_count[item.item_code] = count

    def increase_stock(self, item_code: str, count: int):
        with self.lock:
            self.item_count[item_code] += count

    def dispatch_item(self, item_code: str):
        with self.lock:
            if self.item_count[item_code] > 0:
                self.item_count[item_code] -= 1
            else:
                raise Exception("Current Item is out of Stock")

    def hardcode_item_count(self, item_code: str, count: int) :
        """Used in cases when maintaining the vending machine."""
        with self.lock:
            self.item_count[item_code] = count

    def is_available(self, item_code: str) -> bool:
        with self.lock:
            return self.item_count[item_code] > 0

    def get_item_by_code(self, item_code) -> Optional[Item]:
        with self.lock:
            if item_code not in self.item_map:
                print("Item not present in the given rack.")
                return None
            return self.item_map[item_code]


class VendingMachineState(ABC):
    def __init__(self, machine: 'VendingMachine'):
        self.machine = machine

    def select_item(self, item: Item):
        pass

    def insert_money(self, money: Money):
        pass

    def refund(self):
        pass

    def dispense(self):
        pass

class IdleState(VendingMachineState):
    def select_item(self, item: Item):
        self.machine.selected_item = item
        self.machine.set_current_state(ItemSelectedState(self.machine))

    def insert_money(self, money: Money):
        print("Please select an item first")

    def refund(self):
        print("Please select item first")

    def dispense(self):
        print("Please select item first")

class ItemSelectedState(VendingMachineState):
    def select_item(self, item: Item):
        print("Item is already Selected")

    def insert_money(self, money: Money) :
        self.machine.current_balance += money
        print(f"Inserted {money}. Current balance: {self.machine.get_current_balance()}")
        if self.machine.check_has_sufficient_balance():
            print("Enough money inserted")
            self.machine.set_current_state(SufficientMoneyState(self.machine))

    def refund(self):
        self.machine.refund_amount()
        self.machine.set_idle_state()
        print("Amount refunded")

    def dispense(self):
        print("Enough Money not available. Insert money first.")

class SufficientMoneyState(VendingMachineState):
    def select_item(self, item: Item):
        print("Item is already Selected")

    def insert_money(self, money: Money):
        print(f"Inserted {money}. Current balance: {self.machine.get_current_balance()}")
        self.machine.current_balance += money

    def refund(self):
        self.machine.refund_amount()
        self.machine.set_idle_state()
        print("Amount refunded")

    def dispense(self):
        selected_item = self.machine.get_selected_item()
        if not selected_item:
            print("No item has selected.")
            return
        if not self.machine.check_has_sufficient_balance():
            print("Machine does not have enough balance")
            return
        if not self.machine.inventory.is_available(self.machine.get_selected_item().item_code):
            print("Does not have enough stock for the given item")
            return

        self.machine.inventory.dispatch_item(self.machine.get_selected_item().item_code)
        print("Item dispensed")
        self.machine.deduct_item_money()
        self.machine.refund_amount()
        self.machine.set_idle_state()


class VendingMachine:
    def __init__(self):
        self.current_balance: float = 0
        self.selected_item: Optional[Item] = None
        self.current_state: VendingMachineState = IdleState(self)
        self.inventory: Inventory = Inventory()
        self.balance_lock = threading.Lock()
        self.state_lock = threading.Lock()

    def refund(self):
        self.current_state.refund()

    def refund_amount(self):
        print(f"Refunding amount: {self.current_balance}")
        with self.balance_lock:
            self.current_balance = 0

    def check_has_sufficient_balance(self) -> bool:
        if self.current_balance >= self.selected_item.cost:
            return True
        return False

    def deduct_item_money(self):
        with self.balance_lock:
            if self.current_balance >= self.selected_item.cost:
                self.current_balance -= self.selected_item.cost
            else:
                raise Exception("Enough balance not available")

    def get_selected_item(self) -> Item:
        return self.selected_item

    def get_current_balance(self) -> float:
        return self.current_balance

    def add_item(self, item_code: str, name: str, cost: float, count: int):
        item = Item(name, item_code, cost)
        self.inventory.add_item_object(item, count)

    def set_current_state(self, state: VendingMachineState):
        with self.state_lock:
            self.current_state = state

    def set_idle_state(self):
        with self.balance_lock:
            self.set_current_state(IdleState(self))
            self.selected_item = None
            self.current_balance = 0

    def select_item(self, item_code: str):
        item = self.inventory.get_item_by_code(item_code)
        if not self.inventory.is_available(item_code):
            print("Selected item not available")
            return
        self.current_state.select_item(item)

    def insert_money(self, amount: Money):
        self.current_state.insert_money(amount)

    def buy(self):
        self.current_state.dispense()

    def dispense(self):
        self.current_state.dispense()



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
    machine.refund()

    print("\n---\n")

    print("Scenario 3: Refund")
    machine.select_item("A2")
    machine.insert_money(Money.TWENTY)
    machine.refund()

    print("\n---\n")

    print("Scenario 4: Out of stock")
    machine.select_item("A1")
    machine.insert_money(Money.TEN)
    machine.insert_money(Money.TWENTY)
    machine.insert_money(Money.FIFTY)
    machine.dispense()
