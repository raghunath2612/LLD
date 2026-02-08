class Vehicle:
    def __init__(self, brand: str, model: str, year: int):
        self.brand = brand
        self.model = model
        self.year = year

    def start(self):
        print(f"Vehicle with brand: {self.brand} and model: {self.model} started")

class MotorBike(Vehicle):
    def __init__(self, brand: str, model: str, year: int, type: str):
        super().__init__(brand, model, year)
        self.type = type

    def start(self):
        print(f"Bike with brand: {self.brand} and model: {self.model} started")


bike = MotorBike('Honda', 'Activa', 2021, 'City')
bike.start()
