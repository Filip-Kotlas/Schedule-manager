"""Contains a class for the main window of the program."""
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
import platform
from typing import List
import pickle
from pathlib import Path
import os

from PIL import Image, ImageTk

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
        self.window.title(config.APP_NAME)
        self.set_window_geometry()
        self.win_size = (0, 0)
        self.current_screen_state = utilities.ScreenState.SCHEDULE_LIST_SHOWN
        self.initialize_menu()
        self.schedules: List[Schedule] = []
        self.load_schedules(config.SCHEDULE_FOLDER_PATH)
        self.painter = SchedulePainter()
        self.painter.change_schedule(Schedule(""))
        self.tk_image = ImageTk.PhotoImage(self.painter.get_image())

        def on_resize(event) -> None:
            if self.current_screen_state == utilities.ScreenState.SCHEDULE_DRAWN:
                if str(event.widget) == ".": # . is toplevel window
                    if self.win_size != (event.width, event.height):
                        self.win_size = (event.width, event.height)
                        self.show_schedule()

        self.window.bind("<Configure>", func=on_resize)

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
        schedule_menu.add_command(label="Otevřít", command=self.load_extra_schedule, accelerator=f"{modifier_name}+O")
        schedule_menu.add_command(label="Uložit", command=self.save_schedule, accelerator=f"{modifier_name}+S")
        schedule_menu.add_command(label="Uložit jako", command=self.save_schedule_as, accelerator=f"{modifier_name}+Shift+S")

        menu_bar.add_command(label="Hodiny", command=self.manage_lessons)
        menu_bar.add_command(label="Nastavení", command=self.open_settings)

        self.window.config(menu=menu_bar)

        self.window.bind(f"<{modifier}-v>", lambda event: self.display_schedule_list())
        self.window.bind(f"<{modifier}-n>", lambda event: self.create_schedule())
        self.window.bind(f"<{modifier}-s>", lambda event: self.save_schedule())
        self.window.bind(f"<{modifier}-Shift-S>", lambda event: self.save_schedule_as())
        self.window.bind(f"<{modifier}-o>", lambda event: self.load_extra_schedule())
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

        Renames the schedule with given index. If the schedule is from the default schedule folder 
        then it is renamed there to.
        
        Args:
            index (int): The index of the schedule to be renamed.
        """
        new_name = simpledialog.askstring(title="Přejmenovat",
                                          prompt="Jméno",
                                          initialvalue=self.schedules[index].name)
        if new_name:
            if os.path.exists(config.SCHEDULE_FOLDER_PATH / f"{self.schedules[index].name}.txt"):
                os.rename(config.SCHEDULE_FOLDER_PATH / f"{self.schedules[index].name}.txt",
                          config.SCHEDULE_FOLDER_PATH / f"{new_name}.txt")

            self.schedules[index].rename(new_name)
            self.display_schedule_list()

    def delete_schedule(self, index: int) -> None:
        """
        Deletes the chosen schedule from the schedule list and from the default schedule folder.
        
        First shows dialog window and asks for confirmation. Then deletes the schedule.

        Args:
            index (int): The index of the schedule to be deleted.
        """
        confirm = messagebox.askyesno(title="Potvrdit",
                                      message=f"Opravdu chcete smazat rozvrh {self.schedules[index].name}?")
        if confirm:
            file_path = config.SCHEDULE_FOLDER_PATH / f"{self.schedules[index].name}.txt"
            if os.path.exists(file_path):
                os.remove(file_path)
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

        canvas_frame = tk.Frame(self.window)
        canvas_frame.pack(pady=10, padx=10, fill="both", expand=True)
        canvas_frame.update_idletasks()

        settings = utilities.load_settings(config.SETTINGS_PATH)

        image_ratio = settings["schedule_width"]/float(settings["schedule_height"])
        canvas_frame_ratio = canvas_frame.winfo_width()/float(canvas_frame.winfo_height())
        if image_ratio >= canvas_frame_ratio:
            canvas_width = canvas_frame.winfo_width()
            canvas_height = int(canvas_width / image_ratio)
        else:
            canvas_height = canvas_frame.winfo_height()
            canvas_width = int(canvas_height * image_ratio)

        canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height, background="white")
        self.tk_image = ImageTk.PhotoImage(self.painter.get_image().resize((canvas_width, canvas_height), Image.Resampling.LANCZOS))
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        canvas.place(relx=0.5, rely=0.5, anchor="center")

    def save_schedule(self) -> None:
        """
        Saves the active schedule to the default folder in .txt file.

        First checks whether a schedule is shown, then saves the schedule in .txt file to the folder
        where the schedules will be loaded from on the next start of the application.
        """
        if self.current_screen_state == utilities.ScreenState.SCHEDULE_LIST_SHOWN:
            messagebox.showwarning(title="Nevybrán rozvrh", message="Nejdříve otevřete rozvrh, který chcete uložit.")
            return

        file_path = Path(config.SCHEDULE_FOLDER_PATH) / f"{self.painter.active_schedule.name}.txt"

        self.painter.active_schedule.save_to_txt_file(file_path)

    def save_schedule_as(self) -> None:
        """
        Saves the active schedule to a file.

        First checks wheter a schedule is shown, then dialog window asks where to save the
        schedule. If a destination is chosen, it saves the schedule there. Default destination is
        folder where the schedules will be automatically loaded from on the next start of the
        application.
        """
        if self.current_screen_state == utilities.ScreenState.SCHEDULE_LIST_SHOWN:
            messagebox.showwarning(title="Nevybrán rozvrh", message="Nejdříve otevřete rozvrh, který chcete uložit.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"),
                                                           ("JPEG files", "*.jpg"),
                                                           ("PDF files", "*.pdf"),
                                                           ("TXT file", ".txt")],
                                                initialdir=config.SCHEDULE_FOLDER_PATH,
                                                initialfile="Rozvrh")
        if filename:
            if filename.endswith(".pdf"):
                self.painter.image.save(filename, "PDF")
            elif filename.endswith(".txt"):
                self.painter.active_schedule.save_to_txt_file(filename)
            else:
                self.painter.image.save(filename)

    def load_schedules(self, folder_name: str) -> None:
        """
        Loads all the schedules saved in a folder.

        Checks if the valid folder name was passed. Checks if the .txt files contain valid schedule
        data and then loads the schedules to the schedule list.

        Args:
            folder_name (str): Name of the folder to load the schedules from.
        """
        folder = Path(folder_name)

        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("Složka nenalezena", "Nebyla nalezena složka s rozvrhy!")
            return

        for file in folder.glob("*.txt"):
            try:
                if file:
                    with open(file, 'rb') as schedule_file:
                        schedule = pickle.load(schedule_file)
                    self.schedules.append(schedule)
            except (EOFError, pickle.UnpicklingError):
                messagebox.showerror("Poškozený soubor",
                                     f"Soubor '{file}' je poškozený a nejde načíst.")
            except Exception as e: #TODO: Fix this
                messagebox.showerror("Chyba",
                                     f"Při načítání rozvrhu ze souboru '{file}' došlo k neočekávané chybě: {e}")

    def load_extra_schedule(self) -> None:
        """
        Loads the chosen schedule from a BSON file.

        Shows a dialog window and asks for the file. Then saves the schedule to the list of schedules.
        """
        filename = filedialog.askopenfilename(defaultextension=".txt",
                                              filetypes=[("TXT file", ".txt")])
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
