class Pizza:
    def __init__(self, size: str, crust: str, sauce: str, cheese: str,
                 mushroom=False, pepperoni=False, onions=False):
        self.size = size
        self.crust = crust
        self.sauce = sauce
        self.cheese = cheese
        self.mushroom = mushroom
        self.pepperoni = pepperoni
        self.onions = onions

    def describe(self) -> str:
        toppings = []
        if self.mushroom:
            toppings.append("mushroom")
        if self.pepperoni:
            toppings.append("pepperoni")
        if self.onions:
            toppings.append("onions")
        return (f"size: {self.size}, crust: {self.crust}, sauce: {self.sauce}, cheese: {self.cheese}, "
                f"toppings: {', '.join(toppings) if len(toppings) > 0 else ''}")

# Problem:
# Easy to mistake one value for another key.
# Hard to remember parameter order without correct IDE.
# If you only need to add 2 params, but still forced to pass others.

pizza1 = Pizza("Medium", "thin", "tomato", "mozrella",
               True, False, True)
pizza2 = Pizza(size="Medium", crust="thin", sauce="tomato", cheese="mozrella",
               mushroom=True, pepperoni=False, onions=True)
print(pizza1.describe())