"""
Abstract Factory pattern is mainly used to club elements into one single component.
Ex: If you only need a button for windows, then you can go for Factory pattern.
But in this case you need to create UI which includes multiple components of windows like:
        Button, CheckBox, Radio Button, etc.,
In this case, it's good to go with Abstract factory pattern,
where we will club multiple Factories like, Button, CheckBox, Radio into a single factory.
And then create another factory on top of it like WindowsFactory, MacFactory which will use
        the above created Factories.
"""

from abc import ABC, abstractmethod

class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class CheckBox(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_check_box(self) -> CheckBox:
        pass

class WindowsButton(Button):
    def render(self) -> str:
        return "Rendering Windows Button"

class WindowsCheckBox(CheckBox):
    def render(self) -> str:
        return "Rendering Windows CheckBox"

class MacButton(Button):
    def render(self) -> str:
        return "Rendering Mac Button"

class MacCheckBox(CheckBox):
    def render(self) -> str:
        return "Rendering Mac CheckBox"

class WindowsUIFactory(UIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_check_box(self) -> CheckBox:
        return WindowsCheckBox()

class MacUIFactory(UIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_check_box(self) -> CheckBox:
        return MacCheckBox()

class FactoryProvider:
    @staticmethod
    def get_factory(os_type: str) -> UIFactory:
        if os_type.lower() == "windows":
            return WindowsUIFactory()
        elif os_type.lower() == "mac":
            return MacUIFactory()
        else:
            raise ValueError("Provided OS doesn't exist")


# can create a separate class for this alternatively.
def render_ui(factory: UIFactory):
    button = factory.create_button()
    check_box = factory.create_check_box()
    return [button.render(), check_box.render()]

if __name__ == "__main__":
    factory = FactoryProvider.get_factory("mac")
    rendered_elements = render_ui(factory)
    for x in rendered_elements:
        print(x)