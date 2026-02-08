from abc import ABC, abstractmethod

# After fix
class Eatable(ABC):
    @abstractmethod
    def eat(self) -> str:
        pass

class Workable(ABC):
    @abstractmethod
    def work(self) -> str:
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self) -> str:
        pass


class HumanWorker(Eatable, Workable, Sleepable):
    def eat(self) -> str:
        return "eating"

    def work(self) -> str:
        return "working"

    def sleep(self) -> str:
        return "sleeping"

class RobotWorker(Workable):
    def work(self) -> str:
        return "working"

    # Can create other interfaces like Rechargable and use it here