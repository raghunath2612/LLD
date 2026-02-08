class A:
    def method(self):
        print("In A class")

class B:
    def method(self):
        print("In B class")

"""The order of class names matter in Multiple Inheritance when calling same method"""
class C(A, B):
    pass


c = C()
c.method()