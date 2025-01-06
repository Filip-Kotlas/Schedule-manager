from typing import List
from app.src.lesson import Lesson
import pickle

class Schedule:
    def __init__(self, name):
        self.name = name
        self.lessons: List[Lesson] = []

    def add_lesson(self, lesson: Lesson) -> None:
        self.lessons.append(lesson)

    def remove_lesson(self, lesson: Lesson) -> None:
        print("Not yet ready")
        # TODO: Finish this function

    def save_to_json_file(self, filename: str) -> None:
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
