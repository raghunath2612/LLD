from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    INACTIVE = "inactive"
    PENDING = "pending"

user_status = Status.ACTIVE # Status.ACTIVE
print(user_status) # inactive
print(user_status.value) # ACTIVE
print(user_status.name) # User is Active

if user_status == Status.ACTIVE:
    print("User is Active")
else:
    print("User is InActive")


from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

priority = Priority.CRITICAL
print(priority < priority.MEDIUM)

# Looping through IntEnum
for en in IntEnum:
    print(en)


class Color(Enum):
    RED = (255, 0, 0)
    YELLOW = (0, 255, 0)
    GREEN = (0, 0, 255)
    BLUE = (0, 255, 255)

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def rgb(self):
        return (self.r, self.g, self.b)

    def is_dark(self):
        return self.r + self.b + self.g > 400

color = Color.RED
print(color.rgb()) # (255, 0, 0)
print(color.is_dark()) # False


# Iterating through ENUM
for color in Color:
    print(f"{color.name}: {color.value}")