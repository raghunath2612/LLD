class Person:
    def __init__(self, name, age):
        self.__name = name
        self.__age = age

    def get_age(self):
        return self.__age

    def getName(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def setAge(self, age):
        self.__age = age


person = Person("Raghu", 20)
person.setName("Hero")
print(person.getName()) # Her