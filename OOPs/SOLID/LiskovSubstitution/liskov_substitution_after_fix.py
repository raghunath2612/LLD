from abc import ABC, abstractmethod

# After Liskov Substitution Principle
"""Instead of using fly which the Child Class can't support,
    we can use another method which the child can support"""
class Bird(ABC):
    @abstractmethod
    def move(self) -> str:
        pass

class HummingBird(Bird):
    def move(self) -> str:
        return "Humming Bird Flying"

class Ostritch(Bird):
    def move(self) -> str:
        return "Ostritch Walking"