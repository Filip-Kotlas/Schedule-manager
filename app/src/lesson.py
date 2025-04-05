"""Contains a class for the lessons."""
from datetime import time
from typing import Tuple
from typing import List

from app.utils import utilities

class Lesson:
    """Lesson data structer."""
    def __init__(self,
                 name: str="",
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

    def get_hex_color(self) -> str:
        """Returns color of the lesson in the hexadecimal format.
        
        Returns:
            str: String in format "#RRGGBB".
        """
        return f"#{self.color[0]:02X}{self.color[1]:02X}{self.color[2]:02X}"

    def set_hex_color(self, color: str):
        """
        Sets the color of the class from string in hexadecimal format.

        Args:
            color (str): String in format "#RRGGBB".
        """
        self.color=(int(color[1:3], 16),
                    int(color[3:5], 16),
                    int(color[5:7], 16))

    def has_collision(self, lesson_list: List["Lesson"])-> Tuple[bool, bool]:
        """
        Says whether a lesson is in collision with other lessons.
        
        Args:
            lesson_list (List): List of lessons to compare to.

        Returns: 
            Tuple[bool, bool]: Two boolean values. First says whether the passed lesson has
                collision. Second reports whether the lesson is first.
        """
        collision = False
        first = False
        number_of_collisions = 0
        for index, lesson in enumerate(lesson_list):
            if lesson is not self:
                if (lesson.day == self.day
                    and self.end_time > lesson.start_time
                    and self.start_time < lesson.end_time):
                    collision = True
                    number_of_collisions += 1
                    if self.start_time < lesson.start_time:
                        first = True
                    elif self.start_time == lesson.start_time:
                        first = lesson_list.index(self) < index

        if number_of_collisions >= 2:
            raise Exception("V rozvrhu je hodina s více kolizemi.")
        return collision, first
