import threading
import time
from abc import ABC, abstractmethod
from typing import List, Set, Dict
from enum import Enum

from heapq import heappop, heappush


class Direction(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    IDLE = 'IDLE'

class RequestType(Enum):
    EXTERNAL = 'EXTERNAL'
    INTERNAL = 'INTERNAL'



class Request:
    def __init__(self, floor_no: int, request_type: RequestType, direction: Direction):
        self.floor_no = floor_no
        self.request_type = request_type
        self.direction = direction



class ElevatorManager:
    def __init__(self, strategy: 'ElevatorAssignStrategy'):
        self.elevators: Dict[int, Elevator] = {}
        self.strategy = strategy

    def start(self):
        for elevator_id in self.elevators:
            elevator = self.elevators[elevator_id]
            elevator.start()

    def stop(self):
        for elevator_id in self.elevators:
            elevator = self.elevators[elevator_id]
            elevator.stop()

    def add_elevator(self, elevator: 'Elevator'):
        self.elevators[elevator.id] = elevator

    def request_elevator(self, request: Request):
        elevator = self.strategy.find_elevator(list(self.elevators.values()), request)
        elevator.add_request(request)

class Elevator:
    def __init__(self, elevator_id: int, floor_no: int = 0):
        self.id = elevator_id
        self.floor_no = floor_no
        self.state: ElevatorState = IdleState(self)
        self.up_requests: List[int] = []
        self.down_requests: List[int] = []
        self.observers: List[Subscriber] = []
        self.is_running = False

    def move(self):
        while self.is_running:
            self.state.move()
            time.sleep(0.5)
            for subscriber in self.observers:
                subscriber.subscribe(self.floor_no)

    def add_observer(self, observer: 'Subscriber'):
        self.observers.append(observer)

    def add_down_request(self, floor_no: int):
        heappush(self.down_requests, -floor_no)
        # self.down_requests.add(floor_no)

    def add_up_request(self, floor_no: int):
        heappush(self.up_requests, floor_no)
        # self.up_requests.add(floor_no)

    def add_request(self, request: Request):
        if request.floor_no < self.floor_no:
            self.add_down_request(request.floor_no)
        elif request.floor_no > self.floor_no:
            self.add_up_request(request.floor_no)
        else:
            print("Invalid Input")

    def set_elevator_state(self, state: 'ElevatorState'):
        self.state = state

    def start(self):
        self.is_running = True
        thread = threading.Thread(target=self.move)
        thread.start()
        thread.join()

        # self.move()

    def stop(self):
        self.is_running = False

    def get_direction(self) -> Direction:
        return self.state.get_direction()

class Subscriber(ABC):
    def __init__(self, elevator: Elevator):
        self.elevator = elevator

    @abstractmethod
    def subscribe(self, floor_no: int):
        pass

class Display(Subscriber):
    def subscribe(self, floor_no: int):
        print(f"Display Screen: {self.elevator.id} - {floor_no}")

class ElevatorState(ABC):
    def __init__(self, elevator: Elevator):
        self.elevator = elevator

    @abstractmethod
    def add_input(self, floor_no: int):
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def get_direction(self) -> Direction:
        pass

class IdleState(ElevatorState):
    def add_input(self, floor_no: int):
        if floor_no < self.elevator.floor_no:
            self.elevator.add_down_request(floor_no)
            self.elevator.set_elevator_state(MovingDownState(self.elevator))
        elif floor_no > self.elevator.floor_no:
            self.elevator.add_up_request(floor_no)
            self.elevator.set_elevator_state(MovingUpState(self.elevator))
        else:
            print("Invalid Input.")

    def move(self):
        pass

    def get_direction(self) -> Direction:
        return Direction.IDLE


class MovingUpState(ElevatorState):
    def add_input(self, floor_no: int):
        if floor_no < self.elevator.floor_no:
            self.elevator.add_down_request(floor_no)
        elif floor_no > self.elevator.floor_no:
            self.elevator.add_up_request(floor_no)

    def move(self):
        if self.elevator.up_requests:
            next_level = self.elevator.up_requests[0]
            self.elevator.floor_no += 1
            while self.elevator.floor_no == next_level:
                heappop(self.elevator.up_requests)
        elif self.elevator.down_requests:
            self.elevator.set_elevator_state(MovingDownState(self.elevator))
        else:
            self.elevator.set_elevator_state(IdleState(self.elevator))

    def get_direction(self) -> Direction:
        return Direction.UP


class MovingDownState(ElevatorState):
    def add_input(self, floor_no: int):
        if floor_no < self.elevator.floor_no:
            self.elevator.add_down_request(floor_no)
        elif floor_no > self.elevator.floor_no:
            self.elevator.add_up_request(floor_no)

    def move(self):
        if self.elevator.down_requests:
            next_level = self.elevator.down_requests[0]
            self.elevator.floor_no -= 1
            while self.elevator.floor_no == next_level:
                heappop(self.elevator.down_requests)
        elif self.elevator.up_requests:
            self.elevator.set_elevator_state(MovingUpState(self.elevator))
        else:
            self.elevator.set_elevator_state(IdleState(self.elevator))

    def get_direction(self) -> Direction:
        return Direction.DOWN


class ElevatorAssignStrategy(ABC):
    @abstractmethod
    def find_elevator(self, elevators: List[Elevator], request: Request) -> Elevator:
        pass


# It would be challenging to write this working code in interview.
# So, say one would be fine. Will add more later if time permits
class IdleElevatorStrategy(ElevatorAssignStrategy):
    def find_elevator(self, elevators: List[Elevator], request: Request) -> Elevator:
        idle_elevators = [e for e in elevators if e.get_direction() == Direction.IDLE]
        return idle_elevators[0]

if __name__ == "__main__":
    print("=== Elevator System Demo ===\n")

    # Create elevator system
    system = ElevatorManager(IdleElevatorStrategy())

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

