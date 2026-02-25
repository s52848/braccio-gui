from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout


class MainLayout(BoxLayout):
    label_text = StringProperty("Witaj w aplikacji!")

    def on_button_click(self, number):
        self.label_text = f"Naciśnięto przycisk {number}"


class MyApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    MyApp().run()
