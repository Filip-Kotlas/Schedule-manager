from typing import List
from app.src.course import Course

class Schedule:
    def __init__(self, name):
        self.name = name
        self.courses: List[Course] = []

    def add_course(self, course: Course) -> None:
        self.courses.append(course)

    def remove_course(self, course: Course) -> None:
        print("Not yet ready")
        # TODO: Finish this function