from typing import Dict, Any
import time

class Document:
    def __init__(self, template_name: str, user_data: Dict):
        self.template_name = template_name
        self.user_data = user_data
        self.load_template_data()
        self.load_user_info()
        self.format_document()

    def load_template_data(self) -> None:
        time.sleep(1) # Expensive db operation
        print("Loaded template data")

    def load_user_info(self) -> None:
        time.sleep(2) # Expensive network operation
        print("Loaded User Info")

    def format_document(self) -> None:
        time.sleep(1) # Expensive server processing task
        print("Formatted Document")

doc1 = Document("release-notes", {"id": 1, "username": "raghu"})
doc2 = Document("kba", {"id": 2, "username": "john"})
# Here we are just modifying the user info for the document.
# Document is not related to user info.
# So, creating a prototype for each document will save a lot of time
doc3 = Document("releas-notes", {"id": 3, "user_name":"paul"})