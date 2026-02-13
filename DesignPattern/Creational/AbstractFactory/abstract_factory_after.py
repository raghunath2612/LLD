from abc import ABC, abstractmethod
from typing import List


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
        return "Rendering windows Button"


class WindowsCheckBox(CheckBox):
    def render(self) -> str:
        return "Rendering Checkbox"


class MacButton(Button):
    def render(self) -> str:
        return "Rendering Mac Button"


class MacCheckBox(CheckBox):
    def render(self) -> str:
        return "Rendering CheckBox"


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
            raise ValueError("Invalid OS type")


def create_ui(os_type: str) -> List[str]:
    os_factory = FactoryProvider.get_factory(os_type)
    return [os_factory.create_button.render(), os_factory.create_check_box.render()]

created_ui = create_ui("windows")
for x in created_ui:
    print(x, end=" ")