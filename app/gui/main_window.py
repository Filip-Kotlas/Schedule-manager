import tkinter as tk
import tkinter.ttk as ttk
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
        self.schedules.append(Schedule("Rozvrh 2"))
        self.schedules.append(Schedule("Rozvrh 3"))
        self.painter = SchedulePainter(self.root)

        self.display_schedule_list()

    def initialize_menu(self) -> None:
        menu_bar = tk.Menu(self.root)

        menu_bar.add_command(label="Rozvrhy", command=self.display_schedule_list)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Nový")
        file_menu.add_command(label="Otevřít")
        file_menu.add_command(label="Uložit jako...")
        file_menu.add_command(label="Uložit")
        menu_bar.add_cascade(label="Soubor", menu=file_menu)

        menu_bar.add_command(label="Nastavení", command=self.open_settings)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Ukaž pomoc")
        menu_bar.add_cascade(label="Pomoc", menu=help_menu)

        self.root.config(menu=menu_bar)

        # TODO: Add all the functionality
        # TODO: Add shortcuts
        # TODO: Improve details
        # NOTE: https://www.tutorialspoint.com/python/tk_menu.htm

    def open_settings(self) -> None:
        #TODO: Možná tuhle funkci přejmenovat.
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Nastavení")
        settings_window.resizable(False, False)
        settings_window.grab_set()
        settings_window.transient(self.root)
        settings = utilities.load_settings()

        # visuals ie. width, height, orientation
        wrapper_visuals = tk.Frame(settings_window)
        wrapper_visuals.grid(row=0, column=0, padx=10, pady=10)

        width_label = tk.Label(wrapper_visuals, text="Šířka rozvrhu:")
        width_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        width_entry = tk.Entry(wrapper_visuals)
        width_entry.insert(0, str(settings["schedule_width"]))
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        
        height_label = tk.Label(wrapper_visuals, text="Výška rozvrhu:")
        height_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        height_entry = tk.Entry(wrapper_visuals)
        height_entry.insert(0, str(settings["schedule_height"]))
        height_entry.grid(row=1, column=1, padx=5, pady=5)

        orientation_label = tk.Label(wrapper_visuals, text="Orientace rozvrhu")
        orientation_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        wrapper_orientation = tk.Frame(wrapper_visuals)
        wrapper_orientation.grid(row=2, column=1, padx=5, pady=5)
        orientation = tk.StringVar(value=settings["schedule_orientation"])
        horizontal_radio_button = tk.Radiobutton(wrapper_orientation, text="Horizontal", variable=orientation, value="horizontal")
        vertical_radio_button = tk.Radiobutton(wrapper_orientation, text="Vertical", variable=orientation, value="vertical")
        horizontal_radio_button.pack(anchor="w")
        vertical_radio_button.pack(anchor="w")

        # times ie. start of the days, end of the days, days of the week
        wrapper_times = tk.Frame(settings_window)
        wrapper_times.grid(row=0, column=1, padx=10, pady=10)

        day_start_label = tk.Label(wrapper_times, text="Začátek dne:")
        day_start_label.grid(row=0, column=0, sticky="w")
        start_time = tk.StringVar()
        start_time.set(settings["day_start"])
        times = [f"{i:02}:{j:02}" for i in range(24) for j in (0, 30)]
        start_time_combobox = ttk.Combobox(wrapper_times, textvariable=start_time, values=times, state="readonly")
        start_time_combobox.grid(row=0, column=1)

        day_end_label = tk.Label(wrapper_times, text="Konec dne:")
        day_end_label.grid(row=1, column=0, sticky="w")
        end_time = tk.StringVar()
        end_time.set(settings["day_end"])
        end_time_combobox = ttk.Combobox(wrapper_times, textvariable=end_time, values=times, state="readonly")
        end_time_combobox.grid(row=1, column=1)

        choice_of_days_label = tk.Label(wrapper_times, text="Dny v týdnu:")
        choice_of_days_label.grid(row=2, column = 0, sticky="w")
        wrapper_days = tk.Frame(wrapper_times)
        wrapper_days.grid(row=2, column=1)

        days = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
        days_variables = []
        for index, day in enumerate(days):
            day_var = tk.BooleanVar()
            days_variables.append(day_var)

            if settings["days_in_week"][index] == "1":
                day_var.set(1)
            else:
                day_var.set(0)

            day_check_button = tk.Checkbutton(wrapper_days, text=day, variable=day_var)
            day_check_button.pack()

        def save_settings(settings: Dict) -> None:
            settings["schedule_width"] = int(width_entry.get())
            settings["schedule_height"] = int(height_entry.get())
            settings["schedule_orientation"] = orientation.get()
            settings["day_start"] = start_time.get()
            settings["day_end"] = end_time.get()
            settings["days_in_week"] = 0
            settings["days_in_week"] = ""
            for i, var in enumerate(days_variables):
                if var.get() == 1:
                    settings["days_in_week"] += "1"
                else:
                    settings["days_in_week"] += "0"

            utilities.update_settings(settings)
            self.painter.update()
            if self.current_screen_state == ScreenState.SCHEDULE_DRAWN:
                self.draw_schedule()
                self.show_schedule()
            settings_window.destroy()

        # TODO: Přidat možnost zmáčknout enter, která udělá to samé, co save_button.
        # TODO: Přidat kontrolu vstupů.
        # TODO: Finálně vyřešit, jak to má vypadat.
        save_button = tk.Button(settings_window, text="Uložit", command=lambda sett=settings: save_settings(sett))
        save_button.grid(row=3, columnspan=2)

        self.root.wait_window(settings_window)

    def clear_window(self) -> None:
        for widget in self.root.winfo_children():
            if widget.winfo_class() == "Canvas" or widget.winfo_class() == "Scrollbar":
                widget.grid_forget()
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

        self.current_screen_state = ScreenState.SCHEDULE_LIST_SHOWN
        #TODO: Finish

    def open_schedule(self, index: int) -> None:
        self.clear_window()
        self.draw_schedule(True, index)
        self.show_schedule()
        self.current_screen_state = ScreenState.SCHEDULE_DRAWN

    def edit_schedule(self, index: int) -> None:
        print("Editing")
        #TODO: Finish

    def delete_schedule(self, index: int) -> None:
        self.schedules.pop(index)
        self.display_schedule_list()

    def draw_schedule(self, change_schedule: bool=False, index: int=0) -> None:
        if change_schedule:
            self.painter.change_schedule(self.schedules[index])
        self.painter.draw()

    def show_schedule(self) -> None:
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        self.painter.canvas.grid(row=0, column=0)

        horizontal_scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.painter.canvas.xview)
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        vertical_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.painter.canvas.yview)
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        self.painter.canvas.configure(xscrollcommand=horizontal_scrollbar.set,
                                   yscrollcommand=vertical_scrollbar.set,
                                   scrollregion=(0, 0, int(self.painter.canvas.cget("width")), int(self.painter.canvas.cget("height"))))

    def run(self) -> None:
        self.root.mainloop()

class ScreenState(Enum):
    SCHEDULE_DRAWN = 0
    SCHEDULE_LIST_SHOWN = 1
