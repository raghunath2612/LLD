"""Python does not have true access modifiers
it relies on naming conventions and developer discipline."""

class Person:
    def __init__(self, name):
        self.name = name # Public

class Person2:
    def __init__(self, name):
        self._name = name # Protected

class Person3:
    def __init__(self, name):
        self.__name = name # Private