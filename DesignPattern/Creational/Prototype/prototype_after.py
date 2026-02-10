from abc import ABC, abstractmethod
from typing import Any, Dict
import time
import copy

class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

class DocumentPrototype(ABC):
    @abstractmethod
    def clone(self) -> 'DocumentPrototype':
        pass

    @abstractmethod
    def configure(self, user_data: User) -> None:
        pass


class Document(DocumentPrototype):
    def __init__(self, template_name: str, user_data: User=None):
        self.template_name = template_name
        self.user_data = user_data
        self.load_template_data()
        self.format_document()

    def load_template_data(self) -> None:
        time.sleep(1) # Expensive db operation
        print("Loaded template data")

    def format_document(self) -> None:
        time.sleep(1) # Expensive server processing task
        print("Formatted Document")

    def clone(self) -> DocumentPrototype:
        print("Creating clone of object")
        return copy.copy(self)

    def configure(self, user_data: User) -> None:
        self.user_data = user_data
        print("Configured Document")

class DocumentPrototypeRegistry:
    def __init__(self):
        self.prototypes:Dict[str, DocumentPrototype] = {}

    def register(self, document):
        self.prototypes[document.template_name] = document

    def get_prototype(self, template_name):
        if template_name not in self.prototypes:
            raise ValueError("Given template_name not present in available prototypes")
        return self.prototypes[template_name].clone()

def main():


    doc1 = Document("release-notes")
    doc2 = Document("kba")

    # Here we created prototype for already created objects
    registry = DocumentPrototypeRegistry()
    registry.register(doc1)
    registry.register(doc2)

    user1 = User(user_id=1, username="raghu")
    user2 = User(user_id=2, username="john")

    # Fetching the already created objects and then reusing them
    prototype1 = registry.get_prototype("release-notes")
    prototype2 = registry.get_prototype("kba")
    prototype3 = registry.get_prototype("release-notes")

    prototype1.configure(user1)
    prototype2.configure(user1)
    prototype3.configure(user2)


if __name__ == "__main__":
    main()