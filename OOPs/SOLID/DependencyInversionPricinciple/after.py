from abc import ABC, abstractmethod

class Switchable(ABC):
    @abstractmethod
    def turn_on(self):
        pass

    @abstractmethod
    def turn_off(self):
        pass

    @abstractmethod
    def is_on(self) -> bool:
        pass

class LightBulb(Switchable):
    def __init__(self):
        self.is_on = False

    def turn_on(self):
        self.is_on = True
        print("Light Bulb turned on")

    def turn_off(self):
        self.is_on = False
        print("Light Bulb turned off")

    def is_on(self) -> bool:
        return self.is_on

class LED(Switchable):
    def __init__(self):
        self.is_on = False

    def turn_on(self):
        self.is_on = True
        print("LED turned on")

    def turn_off(self):
        self.is_on = False
        print("LED turned off")

    def is_on(self) -> bool:
        return self.is_on

class Switch:
    def __init__(self, appliance: Switchable):
        self.appliance = appliance

    def toggle(self):
        if self.appliance.is_on():
            self.appliance.turn_off()
        else:
            self.appliance.turn_on()


led = LED()
switch = Switch(led)
switch.toggle()
switch.toggle()
switch.toggle()