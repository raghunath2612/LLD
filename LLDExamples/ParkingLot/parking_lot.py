import random
from enum import IntEnum
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
from collections import defaultdict

class VehicleSize(IntEnum):
    COMPACT = 1
    REGULAR = 2
    HEAVY = 3


# Interface
class Vehicle(ABC):
    @abstractmethod
    def get_size(self) -> VehicleSize:
        pass

    @abstractmethod
    def get_vehicle_number(self) -> str:
        pass

class MotorCycle(Vehicle):
    def __init__(self, vehicle_number):
        self.vehicle_number = vehicle_number

    def get_size(self) -> VehicleSize:
        return VehicleSize.COMPACT

    def get_vehicle_number(self) -> str:
        return self.vehicle_number

# Create Similar classes for Car, Truck, etc.,


# Interface
class ParkingSpot(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_spot_size(self) -> VehicleSize:
        pass

    @abstractmethod
    def park_vehicle(self, vehicle: Vehicle) -> None:
        pass

    @abstractmethod
    def unpark_vehicle(self) -> None:
        pass

    @abstractmethod
    def get_spot_number(self) -> int:
        pass


class CompactSpot(ParkingSpot):
    def __init__(self, spot_number: int, vehicle: Vehicle=None):
        self.vehicle = vehicle
        self.spot_number = spot_number

    def is_available(self) -> bool:
        return self.vehicle is None

    def get_spot_size(self) -> VehicleSize:
        return VehicleSize.COMPACT

    def park_vehicle(self, vehicle: Vehicle) -> None:
        self.vehicle = vehicle

    def unpark_vehicle(self) -> None:
        self.vehicle = None

    def get_spot_number(self) -> int:
        return self.spot_number

# Create similar for RegularSpot and Heavy Spot

class Ticket:
    def __init__(self, ticket_id: int, entry_time: datetime, parking_spot: ParkingSpot, vehicle: Vehicle,
                 exit_time: datetime=None):
        self.ticket_id = ticket_id
        self.entry_time = entry_time
        self.parking_spot = parking_spot
        self.vehicle = vehicle
        self.exit_time = exit_time

    def calculate_duration_in_mins(self) -> int:
        if self.exit_time is None:
            raise Exception("Exit time not set.")
        delta_time = self.exit_time - self.entry_time
        return int((delta_time.total_seconds()) // 60)


class ParkingManager:
    def __init__(self, compact_vehicles: int, regular_vehicles: int, heavy_vehicles: int):
        self.available_parking_spot_by_size: Dict[VehicleSize, List[ParkingSpot]] = defaultdict(list)
        self.vehicle_to_spot_dict: Dict[str, ParkingSpot] = {}
        self.generate_parking_spots(compact_vehicles, regular_vehicles, heavy_vehicles)

    def generate_parking_spots(self, compact_vehicles: int, regular_vehicles: int, heavy_vehicles: int):
        for i in range(1, compact_vehicles + 1):
            self.available_parking_spot_by_size[VehicleSize.COMPACT].append(CompactSpot(i))

        # Similarly add for other 2 types

    def get_parking_spot(self, vehicle: Vehicle) -> ParkingSpot | None:
        for enum_vehicle_size in sorted(VehicleSize, key=lambda x:x.value):
            if vehicle.get_size() <= enum_vehicle_size:
                available_spots = self.available_parking_spot_by_size[enum_vehicle_size]
                if len(available_spots) > 0:
                    return available_spots[0]
        return None

    def park_vehicle(self, vehicle: Vehicle) -> Ticket | None:
        parking_spot = self.get_parking_spot(vehicle)
        if parking_spot is not None:
            if parking_spot.get_spot_size() < vehicle.get_size():
                raise Exception("Provided parking spot is less than Vehicle size")
            parking_spot.park_vehicle(vehicle)
            self.available_parking_spot_by_size[parking_spot.get_spot_size()].remove(parking_spot)
            self.vehicle_to_spot_dict[vehicle.get_vehicle_number()] = parking_spot
            return Ticket(ticket_id=random.randint(1, 100000), entry_time=datetime.now(),
                          parking_spot=parking_spot, vehicle=vehicle)
        return None

    def un_park_vehicle(self, ticket: Ticket) -> None:
        vehicle = ticket.vehicle
        parking_spot = self.vehicle_to_spot_dict[vehicle.get_vehicle_number()]
        parking_spot.unpark_vehicle()
        del self.vehicle_to_spot_dict[vehicle.get_vehicle_number()]
        self.available_parking_spot_by_size[parking_spot.get_spot_size()].append(parking_spot)
        ticket.exit_time = datetime.now()



# Interface
class FareStrategy(ABC):
    @abstractmethod
    def calculate_fare(self, price: int, ticket: Ticket) -> float:
        pass

class BaseFareStrategy(FareStrategy):
    def calculate_fare(self, price: int, ticket: Ticket) -> float:
        vehicle = ticket.vehicle
        if vehicle.get_size() == VehicleSize.COMPACT:
            cost = 0.1
        elif vehicle.get_size() == VehicleSize.REGULAR:
            cost =  0.13
        else:
            cost = 0.15
        return cost * ticket.calculate_duration_in_mins()

class PeakHourFareStrategy(FareStrategy):
    def calculate_fare(self, price: int, ticket: Ticket) -> float:
        if ticket.entry_time.hour > 17:
            return price * 1.5
        return price


class FareCalculator:
    def __init__(self, fare_strategies: List[FareStrategy]):
        self.fare_strategies = fare_strategies

    def calculate_fare(self, ticket: Ticket):
        price = 0
        for strategy in self.fare_strategies:
            price = strategy.calculate_fare(price, ticket)
        return price

class ParkingLot:
    def __init__(self, parking_manager: ParkingManager, fare_calculator: FareCalculator):
        self.parking_manager = parking_manager
        self.fare_calculator = fare_calculator

    def park_vehicle(self, vehicle: Vehicle) -> Ticket:
        ticket = self.parking_manager.park_vehicle(vehicle)
        return ticket

    def unpark_vehicle(self, ticket: Ticket) -> int:
        self.parking_manager.un_park_vehicle(ticket)
        cost = self.fare_calculator.calculate_fare(ticket)
        return cost




def main():
    bike = MotorCycle('1241')
    parking_manager = ParkingManager(10, 10, 10)
    fare_strategies = [BaseFareStrategy(), PeakHourFareStrategy()]
    parking_lot = ParkingLot(parking_manager, FareCalculator(fare_strategies))
    ticket = parking_lot.park_vehicle(vehicle=bike)
    cost = parking_lot.unpark_vehicle(ticket)
    print(f"Cost: {cost}")


if __name__ == '__main__':
    main()