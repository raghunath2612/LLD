class AccessLevel:
    """These private and Protected attributes can still be accessed from outside of this
     class but, developers are expected to respect these access modifiers"""
    def __init__(self, user_name: str, email: str, password: str):
        self.user_name = user_name # Public Variable
        self._email = email # Protected Variable
        self.__password = password # Private Variable

    # Can be used anywhere in the project
    def public(self):
        return "Public"

    # Can be used only in the same class and Child class
    def _protected(self):
        return "Protected"

    # Can be used only inside the class
    def __private(self):
        return "Private"


