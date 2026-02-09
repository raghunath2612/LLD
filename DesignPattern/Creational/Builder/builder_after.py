class Pizza:
    def __init__(self):
        self.size = ""
        self.crust = ""
        self.cheese = ""
        self.sauce = ""
        self.toppings = []

    def describe(self):
        toppings_str = ", ".join(self.toppings)
        return f"size: {self.size}, crust: {self.crust}, sauce: {self.sauce}, cheese: {self.cheese}, toppings: {toppings_str}"

class PizzaBuilder:
    def __init__(self):
        self.pizza = Pizza()

    def with_size(self, size) -> 'PizzaBuilder':
        self.pizza.size = size
        return self

    def with_crust(self, crust) -> 'PizzaBuilder':
        self.pizza.crust = crust
        return self

    # add same for other two

    def add_topping(self, topping) -> 'PizzaBuilder':
        self.pizza.toppings.append(topping)
        return self

    def build(self) -> Pizza:
        if not self.pizza.size:
            raise ValueError("Pizza Size not set")
        if not self.pizza.crust:
            raise ValueError("Pizza crust not set")
        # Raise same for other 2
        return self.pizza


if __name__ == '__main__':
    pizza1 = PizzaBuilder().with_size("small").with_crust("thin").add_topping("pepperoni").build()
    print(pizza1.describe())
