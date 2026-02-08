from abc import ABC, abstractmethod

# Before fix
class Worker(ABC):
    @abstractmethod
    def eat(self) -> str:
        pass

    @abstractmethod
    def work(self) -> str:
        pass

    @abstractmethod
    def sleep(self) -> str:
        pass


class HumanWorker(Worker):
    def eat(self) -> str:
        return "eating"

    def work(self) -> str:
        return "working"

    def sleep(self) -> str:
        return "sleeping"


class RobotWorker(Worker):
    # This is the issue.
    """Here Why to force the child classes to implement
    the functions they dont use
    """
    def eat(self) -> str:
        raise NotImplementedError("Robot's Cant eat")

    def work(self) -> str:
        return "working"

    def sleep(self) -> str:
        raise NotImplementedError("Robot's cant sleep")

