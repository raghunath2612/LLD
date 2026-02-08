class WindowsButton:
    def render(self):
        return "Windows Button Rendr"

class MacButton:
    def render(self):
        return "Mac Button Render"


def click_button(os: str):
    # Problem:
    # Mixing the create and clicking button, which contradicts Factory pattern.
    # Object creation and Business logic shouldn't be in same function
    # It is better to use Abstract classes instead of just functions.
    if os == "windows":
        button = WindowsButton()
    elif os == "mac":
        button = MacButton()
    else:
        raise ValueError("Unknown OS")

    print(button.render())

click_button('windows')



