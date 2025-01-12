"""Contains a class for the main window of the program."""
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
import pickle
from PIL import ImageTk
import platform
from typing import List
from app.utils import config
from app.utils import utilities
from app.src.schedule import Schedule
from app.gui.schedule_painter import SchedulePainter
from app.gui.settings_window import SettingsWindow
from app.gui.lessons_window import LessonsWindow

class MainWindow():
    """The main window of the program."""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Rozvrhář")
        self.set_window_geometry()
        self.current_screen_state = utilities.ScreenState.SCHEDULE_LIST_SHOWN
        self.initialize_menu()
        self.schedules: List[Schedule] = []
        self.painter = SchedulePainter()
        self.painter.change_schedule(Schedule(""))
        self.tk_image = ImageTk.PhotoImage(self.painter.get_image())

        self.display_schedule_list()

    def set_window_geometry(self):
        """
        Sets geometry of the main window.
        
        Sets the window to be in the middle of the screen.
        """
        x_offset = (self.window.winfo_screenwidth() - config.MAIN_WINDOW_INITIAL_SIZE[0])//2
        y_offset = (self.window.winfo_screenheight() - config.MAIN_WINDOW_INITIAL_SIZE[1])//2
        geometry = f"{config.MAIN_WINDOW_INITIAL_SIZE[0]}x{config.MAIN_WINDOW_INITIAL_SIZE[1]}+{x_offset}+{y_offset}"
        self.window.geometry(geometry)

    def initialize_menu(self) -> None:
        """
        Initialises the menu of the main window.
        
        Initialises the menu of the main window and binds the keyboard shortcuts based on the
        operating system.
        """
        if platform.system() == "Darwin":
            modifier_name = "Cmd"
            modifier = "Command"
        elif platform.system() == "Windows" or platform.system() == "Linux":
            modifier_name = "Ctrl"
            modifier = "Control"
        else:
            modifier_name = "Ctrl"
            modifier = "Control"

        menu_bar = tk.Menu(self.window)

        schedule_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Rozvrhy", menu=schedule_menu)
        schedule_menu.add_command(label="Zobrazit", command=self.display_schedule_list, accelerator=f"{modifier_name}+V")
        schedule_menu.add_command(label="Nový", command=self.create_schedule, accelerator=f"{modifier_name}+N")
        schedule_menu.add_command(label="Otevřít", command=self.load_schedule, accelerator=f"{modifier_name}+O")
        schedule_menu.add_command(label="Uložit", command=self.save_schedule_as, accelerator=f"{modifier_name}+S")

        menu_bar.add_command(label="Hodiny", command=self.manage_lessons)
        menu_bar.add_command(label="Nastavení", command=self.open_settings)

        self.window.config(menu=menu_bar)

        self.window.bind(f"<{modifier}-v>", lambda event: self.display_schedule_list())
        self.window.bind(f"<{modifier}-n>", lambda event: self.create_schedule())
        self.window.bind(f"<{modifier}-s>", lambda event: self.save_schedule_as())
        self.window.bind(f"<{modifier}-o>", lambda event: self.load_schedule())
        self.window.bind(f"<{modifier}-t>", lambda event: self.open_settings())
        self.window.bind(f"<{modifier}-h>", lambda event: self.manage_lessons())

    def open_settings(self) -> None:
        """Opens the settings window and then redraws the schedule if it is shown."""
        settings_window = SettingsWindow(self.window)

        self.painter.update()
        if self.current_screen_state == utilities.ScreenState.SCHEDULE_DRAWN:
            self.draw_schedule()
            self.show_schedule()
        settings_window.close()

    def clear_window(self) -> None:
        """Clears all the widgets of the window except for menu."""
        for widget in self.window.winfo_children():
            if widget.winfo_class() != "Menu":
                widget.destroy()

    def display_schedule_list(self) -> None:
        """Displays the list of all loaded schedules."""
        self.clear_window()

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        wrapper = tk.Frame(self.window)
        wrapper.grid(row=1, column=1, sticky="nsew")

        for index, schedule in enumerate(self.schedules):
            frame = tk.Frame(wrapper)
            frame.pack(pady=5, padx=5, fill="x")

            label = tk.Label(frame, text=schedule.name, width=20)
            label.pack(side="left")

            open_button = tk.Button(frame, text="Otevřít", command=lambda i=index: self.open_schedule(i))
            open_button.pack(side="left", padx=5)

            rename_button = tk.Button(frame, text="Přejmenovat", command=lambda i=index: self.rename_schedule(i))
            rename_button.pack(side="left", padx=5)

            delete_button = tk.Button(frame, text="Smazat", command=lambda i=index: self.delete_schedule(i))
            delete_button.pack(side="left", padx=5)

        self.current_screen_state = utilities.ScreenState.SCHEDULE_LIST_SHOWN

    def open_schedule(self, index: int) -> None:
        """
        Opens the chosen schedule.
        
        Args:
            index (int): The index of the schedule to be opened.
        """
        self.clear_window()
        self.draw_schedule(True, index)
        self.show_schedule()
        self.current_screen_state = utilities.ScreenState.SCHEDULE_DRAWN

    def rename_schedule(self, index: int) -> None:
        """
        Renames the chosen schedule.
        
        Args:
            index (int): The index of the schedule to be renamed.
        """
        name = simpledialog.askstring(title="Přejmenovat", prompt="Jméno", initialvalue=self.schedules[index].name)
        if name:
            self.schedules[index].rename(name)
            self.display_schedule_list()

    def delete_schedule(self, index: int) -> None:
        """
        Deletes the chosen schedule.
        
        First shows dialog window and asks for confirmation. Then deletes the schedule.

        Args:
            index (int): The index of the schedule to be deleted.
        """
        confirm = messagebox.askyesno(title="Potvrdit",
                                      message=f"Opravdu chcete smazat rozvrh {self.schedules[index].name}?")
        if confirm:
            self.schedules.pop(index)
            self.display_schedule_list()

    def manage_lessons(self) -> None:
        """
        Opens a window for lessons management.

        First checks wheter a schedule is shown. Then opens a window for lessons management.
        After the window is closed it redraws the schedule
        """
        if self.current_screen_state != utilities.ScreenState.SCHEDULE_DRAWN:
            messagebox.showwarning("Nevybrán rozvrh", "Před úpravou hodin je potřeba vybrat rozvrh.")
            return

        LessonsWindow(self.window, self.painter.active_schedule)
        self.draw_schedule(False)
        self.show_schedule()

    def draw_schedule(self, change_schedule: bool=False, index: int=0) -> None:
        """
        Draws a schedule to the window.

        If demanded changes the drawn schedule. Redraws the schedule in the painter.

        Args:
            change_schedule (bool): If True, drawn schedule is changed.
            index (int): Index of the new schedule to be drawn.
        """
        if change_schedule:
            self.painter.change_schedule(self.schedules[index])
        self.painter.draw()

    def show_schedule(self) -> None:
        """
        Renders the drawn schedule to the screen.

        Sets up the window. Draws the active schedule to the window.
        """
        self.clear_window()
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=0)

        settings = utilities.load_settings(config.SETTINGS_PATH)
        canvas = tk.Canvas(self.window, width=settings["schedule_width"], height=settings["schedule_height"], background="white")
        self.tk_image = ImageTk.PhotoImage(self.painter.get_image())
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        canvas.grid(row=0, column=0)

        horizontal_scrollbar = tk.Scrollbar(self.window, orient="horizontal", command=canvas.xview)
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        vertical_scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        canvas.configure(xscrollcommand=horizontal_scrollbar.set,
                                   yscrollcommand=vertical_scrollbar.set,
                                   scrollregion=(0, 0, int(canvas.cget("width")), int(canvas.cget("height"))))

    def save_schedule_as(self) -> None:
        """
        Saves the active schedule to a file.

        First checks wheter a schedule is shown. Then dialog window and asks where to save the
        schedule. If a destination is chosen, it saves the schedule there.
        """
        if self.current_screen_state == utilities.ScreenState.SCHEDULE_LIST_SHOWN:
            messagebox.showwarning(title="Nevybrán rozvrh", message="Nejdříve otevřete rozvrh, který chcete uložit.")
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

    def load_schedule(self) -> None:
        """
        Loads the schedule from JSON file.

        Shows dialog window and asks for the file. Then saves the schedule to the list of schedules.
        """
        filename = filedialog.askopenfilename(defaultextension=".json",
                                              filetypes=[("JSON file", ".json")])
        if filename:
            with open(filename, 'rb') as file:
                schedule = pickle.load(file)
            self.schedules.append(schedule)
            self.open_schedule(len(self.schedules)-1)

    def create_schedule(self) -> None:
        """
        Creates new empty schedule.
        
        Asks for a name in a dialog window. If a non-empty string is given, it creates the schedule
        with this string as its name.
        """
        name = simpledialog.askstring("Jméno", "Zadejte jméno:")
        if name:
            self.schedules.append(Schedule(name))
            self.open_schedule(len(self.schedules)-1)

    def run(self) -> None:
        """Launches the application."""
        self.window.mainloop()
