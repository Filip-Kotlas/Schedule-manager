import tkinter as tk
from tkinter.ttk import *
from app.utils import config
from app.utils import utilities
from app.src.course import Course
from app.src.schedule import Schedule
import json
from pathlib import Path


class SchedulePainter():

    def __init__(self, parent_widget):
        settings = utilities.load_settings()      
        self.canvas = tk.Canvas(parent_widget, bg="grey", width=settings["schedule_width"], height=settings["schedule_height"])
        self.orientation = settings["schedule_orientation"]
        self.active_schedule = None

    def update(self):
        settings = utilities.load_settings()
        self.canvas.config(width=settings["schedule_width"], height=settings["schedule_height"])
        self.orientation = settings["schedule_orientation"]
    
    def change_schedule(self, schedule: Schedule):
        self.active_schedule = schedule
        # TODO: Možná přidat kontrolu typu. A to i jinde.

    def draw(self):
        if self.orientation == "horizontal":
            self.draw_horizontal()
        elif self.orientation == "vertical":
            self.draw_vertical()
        else:
            print("Error: Wrong orientation")
            # TODO: Raise exception.

    def draw_horizontal(self):
        self.canvas.create_line(0, 0, 200, 200, fill="red")
        # TODO: Finish

    def draw_vertical(self):
        self.canvas.pack(fill='none', expand=False)
        # TODO: Finish


