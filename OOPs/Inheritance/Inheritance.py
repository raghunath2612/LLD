class Vehicle:
    def __init__(self, brand: str, model: str, year: int):
        self.brand = brand
        self.model = model
        self.year = year

    def start(self):
        print(f"{self.brand} {self.model} Started")

    def stop(self):
        print(f"{self.brand} {self.model} Stopped")

    def get_info(self):
        print(f"Brand: {self.brand}, Model: {self.model}, Year: {self.year}")


class Car(Vehicle):
    def __init__(self, brand: str, model: str, year: int, num_doors: int):
        super().__init__(brand, model, year)
        self.num_doors = num_doors

    def honk(self):
        print("Honking")

class Bike(Vehicle):
    def __init__(self, brand: str, model: str, year: int, bike_type: str):
        super().__init__(brand, model, year)
        self.bike_type = bike_type

    def do_wheelie(self):
        print("Doing Wheelie")

vehicle = Vehicle("Toyota", "Fortuner", 2020)
vehicle.start()
vehicle.stop()
bike = Bike("Honda", "Activa", 2021, "scooty")
bike.start()
bike.do_wheelie()
bike.stop()