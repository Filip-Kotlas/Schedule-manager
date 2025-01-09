import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import time
from app.utils import config
from app.utils import utilities
from app.src.lesson import Lesson
from app.src.schedule import Schedule
from app.gui.lesson_form import LessonForm

class LessonsWindow:
    def __init__(self, parent_window, schedule: Schedule):
        self.window = tk.Toplevel(parent_window)
        self.window.geometry(config.lesson_window_initial_size)
        self.window.title("Hodiny")
        self.window.grab_set()
        self.window.transient(parent_window)
        self.schedule = schedule
        self.tree = ttk.Treeview(self.window, columns=("Name", "Place", "Instructor", "Day", "Start", "End"), show="headings")

        self.add_widgets()

        parent_window.wait_window(self.window)

    def add_widgets(self):
        self.tree.pack(fill="both", expand=True, pady=(10, 0))
        self.initialize_treeview()
        self.fill_treeview()

        button_frame = tk.Frame(self.window)
        button_frame.pack(fill="none", side="top", pady=10, padx=10)
        add_button = tk.Button(button_frame, text="Přidat", width=10, command=self.add_lesson)
        add_button.pack(side="left", padx=5)
        edit_button = tk.Button(button_frame, text="Upravit", width=10, command=self.edit_lesson)
        edit_button.pack(side="left", padx=5)
        delete_button = tk.Button(button_frame, text="Smazat", width=10, command=self.delete_lesson)
        delete_button.pack(side="left", padx=5)
        close_button = tk.Button(self.window, text="Zavřít", width=10, command=self.close)
        close_button.pack(side="bottom", padx=5, pady=(0, 5))

    def initialize_treeview(self) -> None:
        self.tree.heading("Name", text="Jméno")
        self.tree.heading("Place", text="Místo")
        self.tree.heading("Instructor", text="Vyučující")
        self.tree.heading("Day", text="Den")
        self.tree.heading("Start", text="Začátek")
        self.tree.heading("End", text="Konec")

        for column in ("Name", "Place", "Instructor", "Day", "Start", "End"):
            self.tree.column(column, width=100)

    def fill_treeview(self) -> None:
        days = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
        for lesson in self.schedule.lessons:
            self.tree.insert("",
                             "end",
                             values=(lesson.name,
                                     lesson.place,
                                     lesson.instructor,
                                     days[lesson.day.value],
                                     lesson.start_time.strftime("%H:%M"),
                                     lesson.end_time.strftime("%H:%M")))

    def add_lesson(self) -> None:
        new_lesson = Lesson("", "", "", utilities.Day.MON, time(8,0), time(9,30), (30, 255, 10))
        form = LessonForm(self.window)
        new_lesson = form.run()
        if new_lesson is None:
            return
        self.schedule.add_lesson(new_lesson)
        self.tree.insert("", "end", values=(new_lesson.name,
                                            new_lesson.place,
                                            new_lesson.instructor,
                                            new_lesson.day,
                                            new_lesson.start_time.strftime("%H:%M"),
                                            new_lesson.end_time.strftime("%H:%M")))

    def edit_lesson(self) -> None:
        selected_lesson = self.tree.selection()
        if not selected_lesson:
            messagebox.showwarning("Hodina nevybrána", "Vyberte hodinu k úpravě.")
            return

        if len(selected_lesson) > 1:
            messagebox.showwarning("Vybráno více hodin", "Označte pouze jednu hodinu.")
            return

        edit_index = self.tree.index(selected_lesson[0])
        edit_lesson = self.schedule.lessons[edit_index]
        form = LessonForm(self.window, edit_lesson)
        edit_lesson = form.run()
        self.schedule.edit_lesson(edit_index, edit_lesson)
        self.tree.item(self.tree.get_children()[edit_index], values=(edit_lesson.name,
                                                                     edit_lesson.place,
                                                                     edit_lesson.instructor,
                                                                     edit_lesson.day,
                                                                     edit_lesson.start_time.strftime("%H:%M"),
                                                                     edit_lesson.end_time.strftime("%H:%M")))

    def delete_lesson(self) -> None:
        selected_lessons = self.tree.selection()
        if not selected_lessons:
            messagebox.showwarning("Hodina nevybrána", "Vyberte hodinu ke smazání.")
            return

        selected_index = (self.tree.index(lesson) for lesson in selected_lessons)
        confirm = messagebox.askyesno("Potvrdit", f"Opravdu chcete vymazat vybrané hodiny? ({len(selected_lessons)})")
        if confirm:
            for index, lesson in zip(selected_index, selected_lessons):
                self.schedule.remove_lesson(index)
                self.tree.delete(lesson)

    def close(self) -> None:
        self.window.destroy()
