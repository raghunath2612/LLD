from abc import ABC, abstractmethod
from typing import List
from enum import Enum
import threading
from heapq import heappush, heappop

class Direction(Enum):
    IDLE = 'IDLE'
    UP = 'UP'
    DOWN = 'DOWN'

class RequestType(Enum):
    EXTERNAL = 'EXTERNAL'
    INTERNAL = 'INTERNAL'


class Request:
    def __init__(self, floor_no: int, direction: Direction, request_type: RequestType):
        self.floor_no = floor_no
        self.direction = direction
        self.request_type = request_type

class ElevatorManager:
    def __init__(self):
        self.elevators: List[Elevator] = []

    def add_elevator(self, elevator: 'Elevator'):
        self.elevators.append(elevator)

    def start(self):
        for elevator in self.elevators:
            elevator.start()

class Elevator:
    def __init__(self, floor_no: int = 0):
        self.floor_no = floor_no
        self.observers: List[Observer] = []
        self.state: ElevatorState = IdleState(self)
        self.up_requests: List[int] = []
        self.down_requests: List[int] = []
        self.is_running = False

    def add_request(self, request: Request):
        self.state.add_request(request)

    def add_observer(self, observer: 'Observer'):
        self.observers.append(observer)

    def move(self):
        thread = threading.Thread(target=self.state.move)
        thread.join()
        while self.is_running:
            thread.start()

    def set_state(self, state: 'ElevatorState'):
        self.state = state

    def start(self):
        self.is_running = True
        self.move()

    def stop(self):
        self.is_running = False


class ElevatorState(ABC):
    def __init__(self, elevator: Elevator):
        self.elevator = elevator

    @abstractmethod
    def add_request(self, request: Request):
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def get_direction(self) -> Direction:
        pass

class IdleState(ElevatorState):
    def add_request(self, request: Request):
        if request.floor_no > self.elevator.floor_no:
            heappush(self.elevator.up_requests, request.floor_no)
            self.elevator.set_state(MovingUpState(self.elevator))
        elif request.floor_no < self.elevator.floor_no:
            heappush(self.elevator.up_requests, -request.floor_no)
            self.elevator.set_state(MovingDownState(self.elevator))
        else:
            print("Invalid input")

    def move(self):
        pass

    def get_direction(self) -> Direction:
        return Direction.IDLE

class MovingUpState(ElevatorState):
    def add_request(self, request: Request):
        if request.floor_no > self.elevator.floor_no:
            heappush(self.elevator.up_requests, request.floor_no)
        elif request.floor_no < self.elevator.floor_no:
            heappush(self.elevator.up_requests, request.floor_no)
        else:
            print("Invalid input")

    def move(self):
        next_floor = heappop(self.elevator.up_requests)
        if next_floor > self.elevator.floor_no:
            self.elevator.floor_no += 1
        elif next_floor == self.elevator.floor_no:
            while self.elevator.up_requests[0] == self.elevator.floor_no:
                heappop(self.elevator.up_requests)
        else:
            print("Invalid floor")


    def get_direction(self) -> Direction:
        return Direction.UP

class MovingDownState(ElevatorState):
    def add_request(self, request: Request):
        if request.floor_no > self.elevator.floor_no:
            heappush(self.elevator.up_requests, request.floor_no)
        elif request.floor_no < self.elevator.floor_no:
            heappush(self.elevator.up_requests, -request.floor_no)
        else:
            print("Invalid input")

    def move(self):
        next_floor = -heappop(self.elevator.down_requests)
        if next_floor < self.elevator.floor_no:
            self.elevator.floor_no -= 1
        elif next_floor == self.elevator.floor_no:
            while self.elevator.up_requests[0] == self.elevator.floor_no:
                heappop(self.elevator.up_requests)
        else:
            print("Invalid floor")

    def get_direction(self) -> Direction:
        return Direction.DOWN

class ElevatorAssignStrategy(ABC):
    pass


class RandomAssignStrategy(ElevatorAssignStrategy):
    pass

class Observer(ABC):
    # Ignore this. Adding this for just to print which observer is having which elevator
    def __init__(self, elevator: Elevator):
        self.elevator = elevator

    @abstractmethod
    def subscribe(self, floor_no: int):
        pass


class Display(Observer):
    def subscribe(self, floor_no: int):
        print(f"Elevator: {self.elevator.floor_no} - {floor_no}")

if __name__ == "__main__":
    print("=== Elevator System Demo ===\n")

    # Create elevator system
    system = ElevatorManager(RandomAssignStrategy())

    # Create elevators
    e1 = Elevator(1)
    e2 = Elevator(2)

    # Add display observers
    e1.add_observer(Display(e1))
    e2.add_observer(Display(e2))

    # Add elevators to system
    system.add_elevator(e1)
    system.add_elevator(e2)

    system.start()

    print("Scenario 1: Request elevator to go up")

    system.request_elevator(Request(5, RequestType.EXTERNAL, Direction.UP))
    # e1.simulate_movement(5)  # Simulate movement to floor 5

    print("\nScenario 2: Request elevator to go down")
    Request(5, RequestType.EXTERNAL, Direction.DOWN)
    system.request_elevator(Request(5, RequestType.EXTERNAL, Direction.DOWN))
    # e1.simulate_movement(3)  # Simulate movement down to floor 2

    print("\nScenario 3: Multiple requests")
    e1.add_request(Request(3, RequestType.INTERNAL, Direction.UP))
    e1.add_request(Request(7, RequestType.INTERNAL, Direction.UP))
    # e1.simulate_movement(5)  # Simulate movement to handle requests

    print("\n=== Demo Complete ===")
