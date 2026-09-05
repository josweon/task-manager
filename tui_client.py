from textual.app import App
from textual.widgets import Static

class TaskManager(App):
    def compose(self):
        yield Static("task-manager")

if __name__ == "__main__":
    TaskManager().run()
