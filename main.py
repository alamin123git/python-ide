import io, os, sys, threading, traceback
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

START = 'print("Hello, World!")\nfor i in range(3):\n    print(i)\n'


class IDE(BoxLayout):
    def __init__(self, path, **kw):
        super().__init__(orientation="vertical", spacing=4, padding=4, **kw)
        self.path = path
        bar = BoxLayout(size_hint_y=None, height=48, spacing=4)
        for text, fn in [("▶ Run", self.run_code), ("Tab", self.tab),
                         ("Save", self.save), ("Clear", self.clear)]:
            bar.add_widget(Button(text=text, on_release=fn))
        self.add_widget(bar)
        self.editor = TextInput(text=START, font_name="RobotoMono-Regular",
                                font_size="15sp", multiline=True,
                                background_color=(0.08, 0.09, 0.11, 1),
                                foreground_color=(0.9, 0.9, 0.9, 1),
                                cursor_color=(1, 1, 1, 1), size_hint_y=0.55)
        self.add_widget(self.editor)
        sv = ScrollView(size_hint_y=0.45)
        self.out = Label(text="Output...", font_name="RobotoMono-Regular",
                         font_size="14sp", size_hint_y=None, halign="left",
                         valign="top", color=(0.5, 1, 0.6, 1))
        self.out.bind(texture_size=lambda i, s: setattr(i, "height", max(s[1], 200)),
                      width=lambda i, w: setattr(i, "text_size", (w, None)))
        sv.add_widget(self.out)
        self.add_widget(sv)
        if os.path.exists(path):
            self.editor.text = open(path, encoding="utf-8").read()

    def tab(self, *a):
        self.editor.insert_text("    ")

    def save(self, *a):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(self.editor.text)
        self.out.text = "Saved ✓"

    def clear(self, *a):
        self.out.text = ""

    def run_code(self, *a):
        self.out.text = "Running...\n"
        threading.Thread(target=self._exec, args=(self.editor.text,), daemon=True).start()

    def _exec(self, code):
        buf = io.StringIO()
        old = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = buf
        try:
            exec(compile(code, "<code>", "exec"), {"__name__": "__main__"})
        except BaseException:
            traceback.print_exc()
        finally:
            sys.stdout, sys.stderr = old
        Clock.schedule_once(lambda dt: setattr(self.out, "text", buf.getvalue() or "(no output)"))


class PythonIDE(App):
    title = "Python IDE"

    def build(self):
        return IDE(os.path.join(self.user_data_dir, "script.py"))


PythonIDE().run()
