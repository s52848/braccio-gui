from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class BraccioRoot(BoxLayout):
    pass


class BraccioApp(App):
    def build(self):
        return BraccioRoot()


if __name__ == "__main__":
    BraccioApp().run()
