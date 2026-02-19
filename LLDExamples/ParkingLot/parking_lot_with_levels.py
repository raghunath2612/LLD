import random
import sys
from collections import defaultdict
from enum import IntEnum
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime

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
    def __init__(self, vehicle_number: str):
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

    @abstractmethod
    def get_floor(self) -> 'Floor':
        pass

    @abstractmethod
    def get_x_position(self) -> int:
        pass

    @abstractmethod
    def get_y_position(self) -> int:
        pass

class Floor:
    def __init__(self, floor_no: int):
        self.floor_no = floor_no
        self.parking_spots: Dict[VehicleSize, List[ParkingSpot]] = defaultdict(list)

    def add_spot(self, size: VehicleSize, spots: List[ParkingSpot]):
        self.parking_spots[size] = spots

    def get_available_spots(self, vehicle_size: VehicleSize) -> List[ParkingSpot]:
        spots = []
        for enum_vehicle_size in sorted(VehicleSize, key=lambda x: x.value):
            if enum_vehicle_size >= vehicle_size:
                spots.extend(self.parking_spots[enum_vehicle_size])

        return spots

    def get_available_spots_by_size(self, vehicle_size: VehicleSize) -> List[ParkingSpot]:
        return self.parking_spots[vehicle_size]

    def park_spot(self, parking_spot: ParkingSpot):
        self.parking_spots[parking_spot.get_spot_size()].remove(parking_spot)

    def release_spot(self, parking_spot: ParkingSpot):
        self.parking_spots[parking_spot.get_spot_size()].append(parking_spot)


class CompactSpot(ParkingSpot):
    def __init__(self, spot_number: int, floor: Floor, x_position: int, y_position: int, vehicle: Vehicle=None):
        self.vehicle = vehicle
        self.floor = floor
        self.spot_number = spot_number
        self.x_position = x_position
        self.y_position = y_position

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

    def get_floor(self) -> Floor:
        return self.floor

    def get_x_position(self) -> int:
        return self.x_position

    def get_y_position(self) -> int:
        return self.y_position


class Entrance:
    def __init__(self, floor: Floor, x_position: int, y_position: int):
        self.floor = floor
        self.x_position = x_position
        self.y_position = y_position


class Ticket:
    def __init__(self, ticket_id: int, entry_time: datetime, parking_spot: ParkingSpot, vehicle: Vehicle,
                 entrance: Entrance, exit_time: datetime=None):
        self.ticket_id = ticket_id
        self.entry_time = entry_time
        self.parking_spot = parking_spot
        self.vehicle = vehicle
        self.entrance = entrance
        self.exit_time = exit_time

    def calculate_duration_in_mins(self) -> int:
        if self.exit_time is None:
            raise Exception("Exit time not set.")
        delta_time = self.exit_time - self.entry_time
        return int((delta_time.total_seconds()) // 60)

class SpotSearchStrategy(ABC):
    @abstractmethod
    def search(self, entrance: Entrance, vehicle: Vehicle, floors: List[Floor]) -> ParkingSpot:
        pass

class SameFloorDefaultSearchStrategy(SpotSearchStrategy):
    """Returns smallest random spot available for vehicle"""
    def search(self, entrance: Entrance, vehicle: Vehicle, floors: List[Floor]) -> ParkingSpot | None:
        floor = entrance.floor
        available_parking_spots = floor.get_available_spots(vehicle.get_size())
        if available_parking_spots:
            return available_parking_spots[0]
        return None

class SameFloorClosestFitSearchStrategy(SpotSearchStrategy):
    """Returns smallest spot available with the closest distance.
        Min Heap option here will become messy as we need to story Min Heap for every entrance.
        It will be better to be only used when we are having at max one entrance per floor"""
    def search(self, entrance: Entrance, vehicle: Vehicle, floors: List[Floor]) -> ParkingSpot | None:
        floor = entrance.floor
        for enum_vehicle_size in sorted(VehicleSize):
            if enum_vehicle_size < vehicle.get_size():
                continue
            available_parking_spots = floor.get_available_spots_by_size(enum_vehicle_size)
            dist = sys.maxsize
            selected_spot = None
            for spot in available_parking_spots:
                new_dist = abs(entrance.x_position - spot.get_x_position()) + abs(entrance.y_position - spot.get_y_position())
                if new_dist < dist:
                    dist = new_dist
                    selected_spot = spot
            if selected_spot:
                return selected_spot
        return None

class MultiFloorClosestFitStrategy(SpotSearchStrategy):
    def __init__(self, search_strategy: SameFloorClosestFitSearchStrategy):
        self.search_strategy = search_strategy

    def search(self, entrance: Entrance, vehicle: Vehicle, floors: List[Floor]) -> ParkingSpot | None:
        floor = entrance.floor
        sorted_floors = sorted(floors, key=lambda f:abs(floor.floor_no - f.floor_no))
        for candidate_floor in sorted_floors:
            spot = self.search_strategy.search(entrance, vehicle, [candidate_floor])
            if spot:
                return spot
        return None





class ParkingManager:
    def __init__(self, floors: List[Floor], search_strategy: SpotSearchStrategy):
        self.floors = floors
        self.vehicle_to_spot_dict: Dict[str, ParkingSpot] = {}
        self.search_strategy = search_strategy

    def get_parking_spot(self, entrance: Entrance, vehicle: Vehicle) -> ParkingSpot | None:
        return self.search_strategy.search(entrance, vehicle, self.floors)

    def park_vehicle(self, entrance: Entrance, vehicle: Vehicle) -> Ticket | None:
        parking_spot = self.get_parking_spot(entrance, vehicle)
        if parking_spot is None:
            return None
        floor = parking_spot.get_floor()
        parking_spot.park_vehicle(vehicle)
        floor.park_spot(parking_spot)
        self.vehicle_to_spot_dict[vehicle.get_vehicle_number()] = parking_spot
        return Ticket(ticket_id=random.randint(1, 100000), entry_time=datetime.now(),
                      parking_spot=parking_spot, vehicle=vehicle, entrance=entrance)

    def un_park_vehicle(self, ticket: Ticket) -> None:
        vehicle = ticket.vehicle
        floor = ticket.parking_spot.get_floor()
        parking_spot = self.vehicle_to_spot_dict[vehicle.get_vehicle_number()]
        parking_spot.unpark_vehicle()
        del self.vehicle_to_spot_dict[vehicle.get_vehicle_number()]
        floor.release_spot(parking_spot)
        ticket.exit_time = datetime.now()

    def get_floor_by_no(self, floor_no) -> Floor | None:
        for floor in self.floors:
            if floor.floor_no == floor_no:
                return floor
        return None


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

    def park_vehicle(self, entrance: Entrance, vehicle: Vehicle) -> Ticket:
        ticket = self.parking_manager.park_vehicle(entrance, vehicle)
        return ticket

    def unpark_vehicle(self, ticket: Ticket) -> int:
        self.parking_manager.un_park_vehicle(ticket)
        cost = self.fare_calculator.calculate_fare(ticket)
        return cost


def main():
    bike = MotorCycle('1241')
    floor1 = Floor(1)
    floor1.add_spot(VehicleSize.COMPACT, [CompactSpot(random.randint(1, 1000000),
                                                      floor1, 1, 2)])
    floor2 = Floor(2)
    floor2.add_spot(VehicleSize.COMPACT, [CompactSpot(random.randint(1, 1000000),
                                                      floor2, 4, 5)])

    parking_manager = ParkingManager([floor1, floor2], SameFloorClosestFitSearchStrategy())
    fare_strategies = [BaseFareStrategy(), PeakHourFareStrategy()]
    parking_lot = ParkingLot(parking_manager, FareCalculator(fare_strategies))
    entrance1 = Entrance(floor1, 10, 20)
    ticket = parking_lot.park_vehicle(entrance=entrance1, vehicle=bike)
    cost = parking_lot.unpark_vehicle(ticket)
    print(f"Cost: {cost}")


if __name__ == '__main__':
    main()

"""
floors: 
Dict[int, Dict[VehicleSize, List[ParkingSpot]]] 
"""