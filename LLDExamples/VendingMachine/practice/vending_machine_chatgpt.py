from collections import defaultdict
from typing import Dict, Optional
from abc import ABC
from enum import IntEnum
import threading


class Money(IntEnum):
    ONE = 1
    TWO = 2
    FIVE = 5
    TEN = 10
    TWENTY = 20
    FIFTY = 50


class Item:
    def __init__(self, name: str, item_code: str, cost: int):
        self.name = name
        self.cost = cost
        self.item_code = item_code


class Inventory:
    def __init__(self):
        self.item_map: Dict[str, Item] = {}
        self.item_count: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()

    def add_item_object(self, item: Item, count: int):
        with self.lock:
            self.item_map[item.item_code] = item
            self.item_count[item.item_code] = count

    def dispatch_item(self, item_code: str):
        with self.lock:
            if self.item_count[item_code] <= 0:
                raise Exception("Out of stock")
            self.item_count[item_code] -= 1

    def get_item(self, item_code: str) -> Optional[Item]:
        with self.lock:
            return self.item_map.get(item_code)


# ---------------- STATE ----------------

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
        if not item:
            print("Invalid item")
            return
        self.machine.set_selected_item(item)
        self.machine.transition_to_item_selected()

    def insert_money(self, money: Money):
        print("Select item first")

    def refund(self):
        print("Nothing to refund")

    def dispense(self):
        print("Select item first")


class ItemSelectedState(VendingMachineState):
    def select_item(self, item: Item):
        print("Item already selected")

    def insert_money(self, money: Money):
        self.machine.add_money(money)

    def refund(self):
        self.machine.refund_and_reset()

    def dispense(self):
        print("Insufficient balance")


class SufficientMoneyState(VendingMachineState):
    def select_item(self, item: Item):
        print("Item already selected")

    def insert_money(self, money: Money):
        self.machine.add_money(money)

    def refund(self):
        self.machine.refund_and_reset()

    def dispense(self):
        self.machine.dispense_item()


# ---------------- MACHINE ----------------

class VendingMachine:
    def __init__(self):
        self.current_balance: int = 0
        self.selected_item: Optional[Item] = None
        self.current_state: VendingMachineState = IdleState(self)
        self.inventory = Inventory()

        # Single lock
        self.lock = threading.Lock()

    # ---------- STATE TRANSITIONS ----------

    def set_selected_item(self, item: Item):
        self.selected_item = item

    def transition_to_item_selected(self):
        self.current_state = ItemSelectedState(self)

    def transition_to_sufficient_money(self):
        self.current_state = SufficientMoneyState(self)

    def reset(self):
        self.current_state = IdleState(self)
        self.selected_item = None
        self.current_balance = 0

    # ---------- BUSINESS LOGIC ----------

    def add_money(self, money: Money):
        self.current_balance += money
        print(f"Inserted {money}, Balance: {self.current_balance}")

        if self.current_balance >= self.selected_item.cost:
            self.transition_to_sufficient_money()

    def refund_and_reset(self):
        print(f"Refunding {self.current_balance}")
        self.reset()

    def dispense_item(self):
        if not self.selected_item:
            print("No item selected")
            return

        try:
            self.inventory.dispatch_item(self.selected_item.item_code)
        except Exception as e:
            print(str(e))
            return

        if self.current_balance < self.selected_item.cost:
            print("Insufficient balance")
            return

        self.current_balance -= self.selected_item.cost
        print("Item dispensed")

        # Return change
        if self.current_balance > 0:
            print(f"Returning change: {self.current_balance}")

        self.reset()

    # ---------- PUBLIC APIs (LOCKED) ----------

    def select_item(self, item_code: str):
        with self.lock:
            item = self.inventory.get_item(item_code)
            self.current_state.select_item(item)

    def insert_money(self, money: Money):
        with self.lock:
            self.current_state.insert_money(money)

    def refund(self):
        with self.lock:
            self.current_state.refund()

    def buy(self):
        with self.lock:
            self.current_state.dispense()

    # ---------- ADMIN ----------

    def add_item(self, item_code: str, name: str, cost: int, count: int):
        item = Item(name, item_code, cost)
        self.inventory.add_item_object(item, count)