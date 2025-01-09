import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from app.utils import utilities

# TODO: Vymazat všude nepotřebné importy.

class SettingsWindow():

    def __init__(self, parent_window: tk.Tk):
        self.window = tk.Toplevel(parent_window)
        self.window.title("Nastavení")
        self.window.resizable(False, False)
        self.window.grab_set()
        self.window.transient(parent_window)
        self.settings = utilities.load_settings()

        self.wrapper_visuals = tk.Frame(self.window) # TODO: Je možné přesunout do těch příslušných funkcí.
        self.wrapper_times = tk.Frame(self.window)

        self.widget_variables = {"width": tk.StringVar(value=str(self.settings["schedule_width"])),
                                 "height": tk.StringVar(value=str(self.settings["schedule_height"])),
                                 "orientation": tk.StringVar(value=self.settings["schedule_orientation"]),
                                 "text_scale": tk.DoubleVar(value=self.settings["text_scale"]),
                                 "start_time": tk.StringVar(),
                                 "end_time": tk.StringVar(),
                                 "days_variables": [tk.BooleanVar() for i in range(7)]}

        self.add_visual_settings()
        self.add_time_settings()

        save_button = tk.Button(self.window, text="Uložit", command=lambda sett=self.settings: self.save_settings())
        save_button.grid(row=3, columnspan=2)

        parent_window.wait_window(self.window)

    def add_visual_settings(self):
        self.wrapper_visuals.grid(row=0, column=0, padx=10, pady=10)

        width_label = tk.Label(self.wrapper_visuals, text="Šířka rozvrhu:")
        width_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        width_entry = tk.Entry(self.wrapper_visuals, textvariable=self.widget_variables["width"])
        width_entry.grid(row=0, column=1, padx=5, pady=5)

        height_label = tk.Label(self.wrapper_visuals, text="Výška rozvrhu:")
        height_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        height_entry = tk.Entry(self.wrapper_visuals, textvariable=self.widget_variables["height"])
        height_entry.grid(row=1, column=1, padx=5, pady=5)

        orientation_label = tk.Label(self.wrapper_visuals, text="Orientace rozvrhu")
        orientation_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        wrapper_orientation = tk.Frame(self.wrapper_visuals)
        wrapper_orientation.grid(row=2, column=1, padx=5, pady=5)
        horizontal_radio_button = tk.Radiobutton(wrapper_orientation,
                                                 text="Horizontal",
                                                 variable=self.widget_variables["orientation"],
                                                 value="horizontal",
                                                 command=self.switch_width_height)
        vertical_radio_button = tk.Radiobutton(wrapper_orientation,
                                               text="Vertical",
                                               variable=self.widget_variables["orientation"],
                                               value="vertical",
                                               command=self.switch_width_height)
        horizontal_radio_button.pack(anchor="w")
        vertical_radio_button.pack(anchor="w")

        text_scale_label = tk.Label(self.wrapper_visuals, text="Škálování textu")
        text_scale_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        text_scale_scale = tk.Scale(self.wrapper_visuals,
                                    from_=0.1,
                                    to=3,
                                    resolution=0.1,
                                    variable=self.widget_variables["text_scale"],
                                    orient="horizontal")
        text_scale_scale.grid(row=3, column=1, padx=5, pady=5)

    def switch_width_height(self):
        temp = self.widget_variables["height"].get()
        self.widget_variables["height"].set(self.widget_variables["width"].get())
        self.widget_variables["width"].set(temp)

    def add_time_settings(self):
        self.wrapper_times.grid(row=0, column=1, padx=10, pady=10)

        day_start_label = tk.Label(self.wrapper_times, text="Začátek dne:")
        day_start_label.grid(row=0, column=0, sticky="w")
        self.widget_variables["start_time"].set(self.settings["day_start"])
        times = [f"{i:02}:00" for i in range(24)]
        start_time_combobox = ttk.Combobox(self.wrapper_times,
                                           textvariable=self.widget_variables["start_time"],
                                           values=times,
                                           state="readonly")
        start_time_combobox.grid(row=0, column=1)

        day_end_label = tk.Label(self.wrapper_times, text="Konec dne:")
        day_end_label.grid(row=1, column=0, sticky="w")
        self.widget_variables["end_time"].set(self.settings["day_end"])
        end_time_combobox = ttk.Combobox(self.wrapper_times,
                                         textvariable=self.widget_variables["end_time"],
                                         values=times,
                                         state="readonly")
        end_time_combobox.grid(row=1, column=1)

        choice_of_days_label = tk.Label(self.wrapper_times, text="Dny v týdnu:")
        choice_of_days_label.grid(row=2, column = 0, sticky="w")
        wrapper_days = tk.Frame(self.wrapper_times)
        wrapper_days.grid(row=2, column=1)

        days = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
        for index, day in enumerate(days):
            if self.settings["days_in_week"][index] == "1":
                self.widget_variables["days_variables"][index].set(1)
            else:
                self.widget_variables["days_variables"][index].set(0)

            day_check_button = tk.Checkbutton(wrapper_days, text=day, variable=self.widget_variables["days_variables"][index])
            day_check_button.pack()

    def save_settings(self) -> None:
        if not str.isdigit(self.widget_variables["width"].get())  or not str.isdigit(self.widget_variables["height"].get()):
            messagebox.showwarning("Nesprávné rozměry", "Rozměry rozvrhu musí být zadány jako celá kladná čísla.")
            return
        self.settings["schedule_width"] = int(self.widget_variables["width"].get())
        self.settings["schedule_height"] = int(self.widget_variables["height"].get())
        self.settings["schedule_orientation"] = self.widget_variables["orientation"].get()
        self.settings["day_start"] = self.widget_variables["start_time"].get()
        self.settings["day_end"] = self.widget_variables["end_time"].get()
        self.settings["days_in_week"] = 0
        self.settings["text_scale"] = self.widget_variables["text_scale"].get()
        self.settings["days_in_week"] = ""
        for var in self.widget_variables["days_variables"]:
            if var.get() == 1:
                self.settings["days_in_week"] += "1"
            else:
                self.settings["days_in_week"] += "0"
        utilities.update_settings(self.settings)
        self.close()

    def close(self) -> None:
        self.window.destroy()
