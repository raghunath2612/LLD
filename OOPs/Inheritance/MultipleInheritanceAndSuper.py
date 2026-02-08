class Bird:
    def fly(self):
        return "flying"

class Swimmable:
    def swim(self):
        return "Swimming"

class Duck(Bird, Swimmable):
    def __init__(self, name: str):
        self.name = name

    def qwack(self):
        return "qwacking"

    def swim(self):
        return f"{self.name} is {super().swim()}"

duck = Duck('duck1')
print(duck.fly())
print(duck.swim())
print()