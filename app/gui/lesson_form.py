"""Contains a class for lesson form window."""
import tkinter as tk
from tkinter import colorchooser
from tkinter import ttk
from tkinter import messagebox
from datetime import time

from app.utils import utilities
from app.src.lesson import Lesson

class LessonForm():
    """The lesson form window."""

    def __init__(self, parent_window: tk.Tk, lesson: Lesson=None) -> None:
        self.window = tk.Toplevel(parent_window)
        self.window.geometry(f"+{self.window.winfo_screenwidth()//4}+{self.window.winfo_screenheight()//8}")
        self.window.resizable(False, False)
        self.window.focus_set()
        self.window.grab_set()
        self.window.transient(parent_window)
        if lesson is None:
            self.window.title("Přidat hodinu")
            lesson = Lesson()
            self.new_lesson = None

        else:
            self.window.title("Upravit hodinu")
            self.new_lesson = lesson

        self.widget_variables = {"name": tk.StringVar(value=lesson.name),
                                 "place": tk.StringVar(value=lesson.place),
                                 "instructor": tk.StringVar(value=lesson.instructor),
                                 "day": tk.StringVar(value=lesson.day),
                                 "start_time_hour": tk.StringVar(value=lesson.start_time.strftime("%H")),
                                 "start_time_minute": tk.StringVar(value=lesson.start_time.strftime("%M")),
                                 "end_time_hour": tk.StringVar(value=lesson.end_time.strftime("%H")),
                                 "end_time_minute": tk.StringVar(value=lesson.end_time.strftime("%M")),
                                 "color": tk.StringVar(value=lesson.get_hex_color())}
        self.window.bind("<Return>", func=lambda event: self.save_lesson())

    def run(self) -> Lesson:
        """
        Launches the lesson form window.
        
        Returns:
            Lesson: New lesson or None if no lesson has been passed to the object during
                initialization and the form was closed without saving.
        """
        self.add_widgets()
        self.window.master.wait_window(self.window)
        return self.new_lesson

    def add_widgets(self) -> None:
        """Adds widgets to the lesson form window."""
        self.add_names_widgets()
        self.add_time_widgets()
        self.add_color_widgets()

        save_button = tk.Button(self.window, text="Uložit", command=self.save_lesson)
        save_button.grid(row=7, columnspan=2, pady=10)

    def add_names_widgets(self) -> None:
        """Adds widgets concerning name, place and instructor to the lesson form window."""
        name_label = tk.Label(self.window, text="Jméno")
        name_entry = tk.Entry(self.window, textvariable=self.widget_variables["name"])
        name_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        place_label = tk.Label(self.window, text="Místo")
        place_entry = tk.Entry(self.window, textvariable=self.widget_variables["place"])
        place_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        place_entry.grid(row=1, column=1, padx=10, pady=5)

        instructor_label = tk.Label(self.window, text="Učitel")
        instructor_entry = tk.Entry(self.window, textvariable=self.widget_variables["instructor"])
        instructor_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        instructor_entry.grid(row=2, column=1, padx=10, pady=5)

    def add_time_widgets(self) -> None:
        """Adds widgets concerning day, start time and end time to the lesson form window."""
        day_label = tk.Label(self.window, text="Den")
        day_options = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
        day_combobox = ttk.Combobox(self.window, textvariable=self.widget_variables["day"], values=day_options, state="readonly" )
        day_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        day_combobox.grid(row=3, column=1, padx=10, pady=5)

        start_time_label = tk.Label(self.window, text="Začátek")
        start_time_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        start_time_wrapper = tk.Frame(self.window)
        start_time_hour_spinbox = tk.Spinbox(start_time_wrapper,
                                             from_=0,
                                             to=23,
                                             textvariable=self.widget_variables["start_time_hour"],
                                             wrap=True,
                                             width=2)
        start_time_colon_label = tk.Label(start_time_wrapper, text=":")
        start_time_minute_spinbox = tk.Spinbox(start_time_wrapper,
                                               from_=0,
                                               to=59,
                                               textvariable=self.widget_variables["start_time_minute"],
                                               wrap=True,
                                               format="%02.0f",
                                               width=2)
        start_time_wrapper.grid(row=4, column=1, padx=10, pady=5)
        start_time_hour_spinbox.pack(side="left", padx=(5, 0))
        start_time_colon_label.pack(side="left", padx = 5)
        start_time_minute_spinbox.pack(side="left", padx = (0, 5))

        end_time_label = tk.Label(self.window, text="Konec")
        end_time_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)
        end_time_wrapper = tk.Frame(self.window)
        end_time_hour_spinbox = tk.Spinbox(end_time_wrapper,
                                           from_=0,
                                           to=23,
                                           textvariable=self.widget_variables["end_time_hour"],
                                           wrap=True,
                                           width=2)
        end_time_colon_label = tk.Label(end_time_wrapper, text=":")
        end_time_minute_spinbox = tk.Spinbox(end_time_wrapper,
                                             from_=0,
                                             to=59,
                                             textvariable=self.widget_variables["end_time_minute"],
                                             wrap=True,
                                             format="%02.0f",
                                             width=2)
        end_time_wrapper.grid(row=5, column=1, padx=10, pady=5)
        end_time_hour_spinbox.pack(side="left", padx=(5, 0))
        end_time_colon_label.pack(side="left", padx = 5)
        end_time_minute_spinbox.pack(side="left", padx = (0, 5))

    def add_color_widgets(self) -> None:
        """Adds widgets concerning color to the lesson form window."""
        color_label = tk.Label(self.window, text="Barva")
        color_wrapper = tk.Frame(self.window)
        current_color_canvas = tk.Canvas(color_wrapper,
                                         bg=self.widget_variables["color"].get(),
                                         width=20,
                                         height=20 )
        choose_color_button = tk.Button(color_wrapper,
                                        text="Vybrat barvu",
                                        command=lambda: self.choose_color(current_color_canvas))
        color_label.grid(row=6, column=0, padx=10, pady=5)
        color_wrapper.grid(row=6, column=1, padx=10, pady=5)
        current_color_canvas.pack(side="left", padx=10)
        choose_color_button.pack(side="left", padx=10)

    def choose_color(self, color_canvas: tk.Canvas) -> None:
        """
        Creates a dialog window for choosing a color.

        Creates a dialog window for color choosing. If the color is chosen, it changes the color of
        the passed canvas. Otherwise it sets the color to red (#FF0000).

        Args:
            color_canvas (tk.Canvas): Canvas to be colored based on the choice of the color.
        """
        color = colorchooser.askcolor(title="Vybrat barvu")

        if color is not None:
            self.widget_variables["color"].set(color[1])
            color_canvas.configure(bg=color[1])
        else:
            self.widget_variables["color"].set("#FF0000")
            color_canvas.configure(bg="#FF0000")

    def save_lesson(self) -> None:
        """
        Saves the inputs to the new lesson.
        
        Saves the inputs to the new lesson and than closes the lesson form window.
        """
        self.new_lesson = Lesson()
        self.new_lesson.name = self.widget_variables["name"].get()
        self.new_lesson.place = self.widget_variables["place"].get()
        self.new_lesson.instructor = self.widget_variables["instructor"].get()
        day = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
        self.new_lesson.day = utilities.Day(day.index(self.widget_variables["day"].get()))
        self.new_lesson.start_time = time(int(self.widget_variables["start_time_hour"].get()),
                                          int(self.widget_variables["start_time_minute"].get()))
        self.new_lesson.end_time = time(int(self.widget_variables["end_time_hour"].get()),
                                        int(self.widget_variables["end_time_minute"].get()))
        self.new_lesson.set_hex_color(self.widget_variables["color"].get())
        if self.new_lesson.start_time < self.new_lesson.end_time:
            self.close()
        else:
            messagebox.showwarning("Špatný čas", "Hodina nesmí začínat později než končí. Změňte čas!")

    def close(self):
        """Closes the lesson form window."""
        self.window.destroy()
