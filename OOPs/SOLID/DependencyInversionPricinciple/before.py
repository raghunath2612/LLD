from abc import ABC, abstractmethod


class LightBulb:
    def __init__(self):
        self.is_on = False

    def turn_on(self):
        self.is_on = True
        print("Bulb turned On")

    def turn_off(self):
        self.is_on = False
        print("Bulb turned off")


class Switch:
    def __init__(self):
        self.bulb = LightBulb()

    def toggle(self):
        if self.bulb.is_on:
            self.bulb.turn_off()
        else:
            self.bulb.turn_on()


light_switch = Switch()
light_switch.toggle() # Bulb turned On
light_switch.toggle() # Bulb turned off
light_switch.toggle() # Bulb turned On

# Here if we want to change the Switch from bulb to Fan.
# We can't do it without changing the structure of Switch.
# So, High level modules should not depend on Low level modules.
# Both should depend on Abstractions

