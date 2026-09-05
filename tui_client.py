from textual.app import App
from textual.screen import Screen
from textual.widgets import Input, Button

class LoginScreen(Screen):
    def compose(self):
        yield Input(placeholder="username", id="username")
        yield Input(placeholder="password", password=True)
        yield Button("Log in", id="login_btn")

    def on_button_pressed(self, event:Button.Pressed):
        username = self.query_one("#username", Input).value
        self.notify(username)


class TaskManager(App):
    SCREENS = {"login": LoginScreen}
    
    def on_mount(self):
        self.push_screen("login")

if __name__ == "__main__":
    TaskManager().run()
