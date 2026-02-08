class User:
    def __init__(self, user_name: str, password: str):
        self.user_name = user_name
        self.__password = password

    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, new_password: str):
        if len(new_password) < 8:
            raise ValueError("Password length must be less than 8 characters")
        self.__password = new_password

user = User('raghu', 'tmp')
print(user.password)
# user.password = 'snns' # Raises error of pwd < 8 chars
user.password = 'wjdnjdsnjsndnjdnj' # Runs successfully