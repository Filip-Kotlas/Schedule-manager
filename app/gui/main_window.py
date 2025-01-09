import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import pickle
from typing import List
from typing import Dict
from datetime import time
from app.utils import config
from app.utils import utilities
from app.src.lesson import Lesson
from app.src.schedule import Schedule
from app.gui.schedule_painter import SchedulePainter
from app.gui.settings_window import SettingsWindow
from app.gui.lessons_window import LessonsWindow

class MainWindow():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.main_window_name)
        self.root.geometry(config.main_window_initial_size)
        self.current_screen_state = utilities.ScreenState.SCHEDULE_LIST_SHOWN
        self.initialize_menu()
        self.schedules: List[Schedule] = []
        self.schedules.append(Schedule("Rozvrh 1"))
        course1 = Lesson("BI-PYT", "T-201", "Bouchala", utilities.Day.THU, time(hour=10, minute=30), time(hour=14, minute=30), (100, 30, 255))
        course2 = Lesson("ANA", "T-203", "Kotlas", utilities.Day.FRI, time(hour=8, minute=30), time(hour=10, minute=30), (255, 30, 100))
        self.schedules[0].lessons.append(course1)
        self.schedules[0].lessons.append(course2)
        self.schedules.append(Schedule("Rozvrh 2"))
        self.schedules.append(Schedule("Rozvrh 3"))
        self.painter = SchedulePainter()

        self.display_schedule_list()

    def initialize_menu(self) -> None:
        menu_bar = tk.Menu(self.root)

        menu_bar.add_command(label="Rozvrhy", command=self.display_schedule_list)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Soubor", menu=file_menu)
        file_menu.add_command(label="Nový", command=self.create_schedule)
        file_menu.add_command(label="Otevřít", command=self.load_schedule)
        file_menu.add_command(label="Uložit jako...", command=self.save_schedule_as)

        menu_bar.add_command(label="Hodiny", command=self.manage_lessons)
        menu_bar.add_command(label="Nastavení", command=self.open_settings)
        menu_bar.add_command(label="Pomoc")

        self.root.config(menu=menu_bar)

        # TODO: Add all the functionality
        # TODO: Add shortcuts
        # TODO: Improve details
        # NOTE: https://www.tutorialspoint.com/python/tk_menu.htm

    def open_settings(self) -> None:
        settings_window = SettingsWindow(self.root)

        self.painter.update()
        if self.current_screen_state == utilities.ScreenState.SCHEDULE_DRAWN:
            self.draw_schedule()
            self.show_schedule()
        settings_window.close()

    def clear_window(self) -> None:
        for widget in self.root.winfo_children():
            if widget.winfo_class() != "Menu":
                widget.destroy()

    def display_schedule_list(self) -> None:
        self.clear_window()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        #https://tkdocs.com/tutorial/grid.html

        wrapper = tk.Frame(self.root)
        wrapper.grid(row=1, column=1, sticky="nsew")

        for index, schedule in enumerate(self.schedules):
            frame = tk.Frame(wrapper)
            frame.pack(pady=5, padx=5, fill="x")

            label = tk.Label(frame, text=schedule.name, width=20)
            label.pack(side="left")

            open_button = tk.Button(frame, text="Open", command=lambda i=index: self.open_schedule(i))
            open_button.pack(side="left", padx=5)

            edit_button = tk.Button(frame, text="Edit", command=lambda i=index: self.edit_schedule(i))
            edit_button.pack(side="left", padx=5)

            delete_button = tk.Button(frame, text="Delete", command=lambda i=index: self.delete_schedule(i))
            delete_button.pack(side="left", padx=5)

        self.current_screen_state = utilities.ScreenState.SCHEDULE_LIST_SHOWN
        #TODO: Finish

    def open_schedule(self, index: int) -> None:
        self.clear_window()
        self.draw_schedule(True, index)
        self.show_schedule()
        self.current_screen_state = utilities.ScreenState.SCHEDULE_DRAWN

    def edit_schedule(self, index: int) -> None:
        print("Editing")
        #TODO: Finish

    def delete_schedule(self, index: int) -> None:
        self.schedules.pop(index)
        self.display_schedule_list()

    def manage_lessons(self) -> None:
        if self.current_screen_state != utilities.ScreenState.SCHEDULE_DRAWN:
            messagebox.showwarning("Nevybrán rozvrh", "Před úpravou hodin je potřeba vybrat rozvrh.")
            return
        LessonsWindow(self.root, self.painter.active_schedule)
        self.draw_schedule(False)
        self.show_schedule()  

    def draw_schedule(self, change_schedule: bool=False, index: int=0) -> None:
        if change_schedule:
            self.painter.change_schedule(self.schedules[index])
        self.painter.draw()

    def show_schedule(self) -> None:
        self.clear_window()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        canvas = self.painter.get_canvas(self.root)
        canvas.grid(row=0, column=0)

        horizontal_scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=canvas.xview)
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        vertical_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        canvas.configure(xscrollcommand=horizontal_scrollbar.set,
                                   yscrollcommand=vertical_scrollbar.set,
                                   scrollregion=(0, 0, int(canvas.cget("width")), int(canvas.cget("height"))))

    def save_schedule_as(self) -> None:
        if self.current_screen_state == utilities.ScreenState.SCHEDULE_LIST_SHOWN:
            messagebox.showwarning(title="Rozvrh nevybrán", message="Nejdříve otevřete rozvrh, který chcete uložit.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"),
                                                           ("JPEG files", "*.jpg"),
                                                           ("PDF files", "*.pdf"),
                                                           ("JSON file", ".json")],
                                                initialfile="Rozvrh")
        if filename:
            if filename.endswith(".pdf"):
                self.painter.image.save(filename, "PDF")
            elif filename.endswith(".json"):
                self.painter.active_schedule.save_to_json_file(filename)
            else:
                self.painter.image.save(filename)
                # TODO: Zkontrolovat, že tohle je správný způsob psaní kódu.

    def load_schedule(self) -> None:
        filename = filedialog.askopenfilename(defaultextension=".json",
                                              filetypes=[("JSON file", ".json")])
        with open(filename, 'rb') as file:
            schedule = pickle.load(file)
        self.schedules.append(schedule)
        self.open_schedule(len(self.schedules)-1)

    def create_schedule(self) -> None:
        name = simpledialog.askstring("Jméno", "Zadejte jméno:")
        if name:
            self.schedules.append(Schedule(name))
            self.open_schedule(len(self.schedules)-1)

    def run(self) -> None:
        self.root.mainloop()
