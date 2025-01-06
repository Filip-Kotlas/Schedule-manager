from datetime import time
from typing import Tuple

class Lesson:
    def __init__(self, name: str, place: str, instructor: str, start_time: time, end_time: time, color: Tuple[int, int, int]):
        self.name = name
        self.place = place
        self.instructor = instructor
        self.start_time = start_time
        self.end_time = end_time
        self.color = color
