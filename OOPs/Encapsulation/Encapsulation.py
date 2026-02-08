class User:
    def __init__(self, user_name: str, password: str):
        self.user_name = user_name
        self._password = password # Same for Private Attributes

    def get_password(self) -> str:
        return self._password

    def set_password(self, password: str):
        self._password = password

user = User('Raghu', 'Temppwd')
print(user.get_password())
user.set_password("NewPwd")
print(user.get_password())
