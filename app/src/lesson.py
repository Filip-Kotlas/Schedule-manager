from datetime import time
from typing import Tuple
from app.utils import utilities

class Lesson:
    def __init__(self, name: str="",
                 place: str="",
                 instructor: str="",
                 day: utilities.Day=utilities.Day.MON,
                 start_time: time=time(8, 0),
                 end_time: time=time(9, 0),
                 color: Tuple[int, int, int]=(255, 0, 0)):
        self.name = name
        self.place = place
        self.instructor = instructor
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.color = color

    def get_hex_color(self):
        return f"#{self.color[0]:02X}{self.color[1]:02X}{self.color[2]:02X}"

    def set_hex_color(self, color: str):
        self.color=(int(color[1:3], 16),
                    int(color[3:5], 16),
                    int(color[5:7], 16))
