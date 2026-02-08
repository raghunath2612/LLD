from abc import ABC, abstractmethod

class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class WindowsButton(Button):
    def render(self) -> str:
        return "Windows Button rendered"

class MacButton(Button):
    def render(self) -> str:
        return "Mac Button rendered"

def create_button(os: str):
    if os.lower() == "windows":
        return WindowsButton()
    elif os.lower() == "mac":
        return MacButton()
    else:
        raise ValueError("Unknown OS")


def click_button(os_type):
    button = create_button(os_type)
    print(button.render())

windows_button = create_button("windows")
windows_button.render()

