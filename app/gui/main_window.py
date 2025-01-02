import tkinter as tk
from app.utils import config

class MainWindow():
    def __init__(self):
        # Inicializace hlavního okna
        self.root = tk.Tk()
        self.root.title(config.main_window_name)
        self.root.geometry(config.main_window_initial_size)

    def run(self):
        # Spuštění hlavní smyčky aplikace
        self.root.mainloop()
