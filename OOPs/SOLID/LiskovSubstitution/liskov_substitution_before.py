#Before Liskov Substitution principe
from abc import ABC, abstractmethod

class Bird(ABC):
	@abstractmethod
	def fly(self) -> str:
		pass

class HummingBird(Bird):
	def fly(self) -> str:
		return "Humming Bird is flying"

class Ostritch(Bird):
	def fly(self) -> str:
		raise Exception("Ostritch cant fly")


