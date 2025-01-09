from typing import List
from app.src.lesson import Lesson
import pickle

class Schedule:
    def __init__(self, name):
        self.name = name
        self.lessons: List[Lesson] = []

    def add_lesson(self, lesson: Lesson) -> None:
        self.lessons.append(lesson)

    def edit_lesson(self, index: int, new_lesson: Lesson) -> None:
        self.lessons[index] = new_lesson

    def remove_lesson(self, index: int) -> None:
        self.lessons.pop(index)

    def save_to_json_file(self, filename: str) -> None:
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
