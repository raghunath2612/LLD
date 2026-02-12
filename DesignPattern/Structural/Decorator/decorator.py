from abc import ABC, abstractmethod

class Coffee(ABC):
    """Coffee interface"""
    @abstractmethod
    def get_price(self) -> int:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

class SimpleCoffee(Coffee):
    """Base object for coffee. Decorator should start from here as base class"""
    def get_price(self) -> int:
        return 5
    def get_description(self) -> str:
        return "Simple Coffee, "

class CoffeeDecorator(Coffee):
    """Decorators to be created on top of Simple coffee.
    We can create n number of decorators, each with its purpose with
        satisfying existing functionality"""
    def __init__(self, coffee: Coffee):
        self.coffee = coffee

    def get_price(self) -> int:
        return self.coffee.get_price()

    def get_description(self) -> str:
        return self.coffee.get_description()

class MilkCoffeeDecorator(CoffeeDecorator):
    def get_price(self) -> int:
        return self.coffee.get_price() + 2
    def get_description(self) -> str:
        return self.coffee.get_description() + "with Milk, "

class SugarCoffeeDecorator(CoffeeDecorator):
    def get_price(self) -> int:
        return self.coffee.get_price() + 1
    def get_description(self) -> str:
        return self.coffee.get_description() + "with Sugar, "

def main():
    simple_coffee = SimpleCoffee()
    print(f"price: {simple_coffee.get_price()}, description: {simple_coffee.get_description()}")

    sugar_coffee = SugarCoffeeDecorator(simple_coffee)
    print(f"price: {sugar_coffee.get_price()}, description: {sugar_coffee.get_description()}")

    sugar_with_milk_coffee = MilkCoffeeDecorator(sugar_coffee)
    print(f"price: {sugar_with_milk_coffee.get_price()}, description: {sugar_with_milk_coffee.get_description()}")

if __name__ == '__main__':
    main()