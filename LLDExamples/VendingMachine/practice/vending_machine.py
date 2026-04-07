from typing import Dict
class Product:
    def __init__(self, product_id: str, product_name: str, cost: int):
        self.product_id = product_id
        self.product_name = product_name
        self.cost = cost


class Rack:
    def __init__(self, rack_id: str, product: Product, count: int):
        self.rack_id = rack_id
        self.product = product
        self.count = count

    def dispense_product(self) -> None:
        if self.count > 0:
            self.count -= 1
            return
        raise Exception("Rack does not have enough Products.")

    def add_products_to_rack(self, count: int) -> None:
        self.count += count


class InventoryManager:
    def __init__(self, racks: Dict[str, Rack]):
        self.racks = racks

    def dispense_product_from_rack(self, rack_id: str):
        if rack_id not in self.racks:
            raise Exception("Rack Id not present in Vending machine Racks")
        rack = self.racks[rack_id]
        rack.dispense_product()

    def add_rack_to_machine(self, rack_id: str, rack: Rack) -> None:
        self.racks[rack_id] = rack

    def delete_rack_from_machine(self, rack_id: str) -> None:
        if rack_id not in self.racks:
            raise Exception("Rack Id not present in Vending machine Racks")
        del self.racks[rack_id]

    def add_products_to_rack(self, rack_id: str, count: int) -> None:
        if rack_id not in self.racks:
            raise Exception("Rack Id not present in Vending machine Racks")
        self.racks[rack_id].add_products_to_rack(count)

    # TODO: Similarly add methods for ` qaszfremoving/emptying racks.


