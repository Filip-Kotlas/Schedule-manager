import tkinter as tk
#from tkinter.ttk import *
#TODO: Přidat toto výše až budu vědět jak.
from typing import List
from typing import Dict
from enum import Enum
from app.utils import config
from app.utils import utilities
from app.src.course import Course
from app.src.schedule import Schedule
from app.gui.schedule_painter import SchedulePainter

class MainWindow():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.main_window_name)
        self.root.geometry(config.main_window_initial_size)
        self.initialize_menu()
        self.schedules: List[Schedule] = []
        self.schedules.append(Schedule("Rozvrh 1"))
        self.schedules.append(Schedule("Rozvrh 356"))
        self.schedules.append(Schedule("Rozvrh 3"))
        self.painter = SchedulePainter(self.root)

        self.current_screen_state = ScreenState.SCHEDULE_LIST_SHOWN
        self.display_schedule_list()

    def initialize_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New File")
        file_menu.add_command(label="Open File")
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Save As...")
        file_menu.add_command(label="Close")

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Show Help")

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.open_settings)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        menu_bar.add_command(label="Settings", command=self.open_settings)
        self.root.config(menu=menu_bar)


        # TODO: Add all the functionality
        # TODO: Add shortcuts
        # TODO: Improve details
        # TODO: Add Settings
        # NOTE: https://www.tutorialspoint.com/python/tk_menu.htm

    def open_settings(self) -> None:
        #TODO: Možná tuhle funkci přejmenovat.
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings = utilities.load_settings()

        width_label = tk.Label(settings_window, text="Schedule width:")
        width_label.grid(row=0, column=0)
        width_entry = tk.Entry(settings_window)
        width_entry.insert(0, str(settings["schedule_width"]))
        width_entry.grid(row=0, column=1)
        
        height_label = tk.Label(settings_window, text="Schedule height")
        height_label.grid(row=1, column=0)
        height_entry = tk.Entry(settings_window)
        height_entry.insert(0, str(settings["schedule_height"]))
        height_entry.grid(row=1, column=1)

        def save_settings(settings: Dict) -> None:
            settings["schedule_width"] = int(width_entry.get())
            settings["schedule_height"] = int(height_entry.get())
            utilities.update_settings(settings)
            self.painter.update()
            if self.current_screen_state == ScreenState.SCHEDULE_DRAWN:
                self.painter.draw()
            settings_window.destroy()

        save_button = tk.Button(settings_window, text="Save", command=lambda sett=settings: save_settings(sett))
        save_button.grid(row=2, columnspan=2)

        self.root.wait_window(settings_window)

    def clear_window(self) -> None:
        for widget in self.root.winfo_children():
            if widget.winfo_class() == "Canvas":
                widget.pack_forget()
            elif widget.winfo_class() != "Menu":
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
        #TODO: Finish

    def open_schedule(self, index: int) -> None:
        self.clear_window()
        self.draw_schedule(index)

    def edit_schedule(self, index: int) -> None:
        print("Editing")
        #TODO: Finish

    def delete_schedule(self, index: int) -> None:
        self.schedules.pop(index)
        self.display_schedule_list()

    def draw_schedule(self, index: int) -> None:
        #self.clear_window()
        self.painter.change_schedule(self.schedules[index])
        self.painter.draw()
        self.current_screen_state = ScreenState.SCHEDULE_DRAWN

    def run(self) -> None:
        self.root.mainloop()

class ScreenState(Enum):
    SCHEDULE_DRAWN = 0
    SCHEDULE_LIST_SHOWN = 1