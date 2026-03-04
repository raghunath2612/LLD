from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict


class VehicleSize(Enum):
    OneByOne = [1, 1]
    TwoByTwo = [2, 2]
    FourByTwo = [4, 2]

class Vehicle(ABC):
    @abstractmethod
    def get_size(self) -> VehicleSize:
        pass

    @abstractmethod
    def get_vehicle_no(self) -> str:
        pass

class Bike(Vehicle):
    def __init__(self, number_plate: str):
        self.number_plate = number_plate

    def get_size(self) -> VehicleSize:
        return VehicleSize.OneByOne

    def get_vehicle_no(self) -> str:
        return self.number_plate


class Car(Vehicle):
    def __init__(self, number_plate: str):
        self.number_plate = number_plate

    def get_size(self):
        return VehicleSize.TwoByTwo

    def get_vehicle_no(self) -> str:
        return self.get_vehicle_no()


class Truck(Vehicle):
    def __init__(self, number_plate: str):
        self.number_plate = number_plate

    def get_size(self):
        return VehicleSize.FourByTwo

    def get_vehicle_no(self) -> str:
        return self.get_vehicle_no()

class ParkingSpot:
    def __init__(self, spot_no: int, x: int, y: int, vehicle: Vehicle=None):
        self.spot_no = spot_no
        self.vehicle = vehicle
        self.x = x
        self.y = y


    def park_spot(self, vehicle: Vehicle):
        self.vehicle = vehicle

    def vacate_spot(self):
        self.vehicle = None

    def is_available(self):
        return self.vehicle is None


class Ticket:
    def __init__(self, vehicle: Vehicle, entry_time: datetime, parking_spot: ParkingSpot,
                 exit_time: datetime = None):
        self.vehicle = vehicle
        self.entry_time = entry_time
        self.parking_spot = parking_spot
        self.exit_time = exit_time

    def calculate_duration_in_mins(self) -> int:
        delta = self.exit_time - self.entry_time
        duration = int(delta.total_seconds() // 60)
        return duration

class ParkingSpotSearchStrategy(ABC):
    @abstractmethod
    def search(self, parking_spots: List[List[ParkingSpot]], vehicle: Vehicle) -> ParkingSpot:
        pass

class DefaultSpotSearchStrategy(ParkingSpotSearchStrategy):
    def check_if_continuous_spots_available(self, i: int, j: int, parking_spots: List[List[ParkingSpot]],
                                            vehicle: Vehicle) -> bool:
        vehicle_size = vehicle.get_size()
        for i1 in range(i, i + vehicle_size.value[0]):
            for j1 in range(j, j + vehicle_size.value[1]):
                if not (0 <= i1 < len(parking_spots) and 0 <= j1 < len(parking_spots[i1]) and parking_spots[i1][j1].is_available()):
                    return False
        return True


    def search(self, parking_spots: List[List[ParkingSpot]], vehicle: Vehicle) -> ParkingSpot | None:
        for i in range(len(parking_spots)):
            for j in range(len(parking_spots[i])):
                is_available = self.check_if_continuous_spots_available(i, j, parking_spots, vehicle)
                if is_available:
                    return parking_spots[i][j]
        return None



class ParkingManager:
    def __init__(self, parking_spots: List[List[ParkingSpot]], search_strategy: ParkingSpotSearchStrategy):
        self.parking_spots = parking_spots
        self.vehicle_to_spot: Dict[str, ParkingSpot] = {}
        self.search_strategy = search_strategy

    def find_parking_spot(self, vehicle: Vehicle) -> ParkingSpot | None:
        return self.search_strategy.search(self.parking_spots, vehicle)

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        parking_spot = self.find_parking_spot(vehicle)
        if parking_spot is None:
            return False
        i, j = parking_spot.x, parking_spot.y
        vehicle_size = vehicle.get_size()
        for i1 in range(i, i + vehicle_size.value[0]):
            for j1 in range(j, j + vehicle_size.value[1]):
                self.parking_spots[i1][j1].park_spot(vehicle)
        return True

    def unpark_vehicle(self, ticket: Ticket) -> bool:
        parking_spot = ticket.parking_spot
        vehicle = ticket.vehicle
        i, j = parking_spot.x, parking_spot.y
        vehicle_size = vehicle.get_size()
        for i1 in range(i, i + vehicle_size.value[0]):
            for j1 in range(j, j + vehicle_size.value[1]):
                self.parking_spots[i1][j1].vacate_spot()
        return True

