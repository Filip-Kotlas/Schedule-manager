"""Contains a class for the schedules."""
import pickle
from typing import List

from app.src.lesson import Lesson

class Schedule:
    """Data structer for the schedules"""
    def __init__(self, name):
        self.name = name
        self.lessons: List[Lesson] = []

    def add_lesson(self, lesson: Lesson) -> None:
        """
        Adds lesson to the schedule.

        Args:
            lesson (Lesson): Lesson to be added.
        """
        self.lessons.append(lesson)

    def edit_lesson(self, index: int, new_lesson: Lesson) -> None:
        """
        Edit lesson in the schedule.

        Args:
            index (int): Index of the lesson in the lessons list to be edited.
            new_lesson (Lesson): New lesson which replaces the old lesson.
        """
        self.lessons[index] = new_lesson

    def remove_lesson(self, index: int) -> None:
        """
        Removes lesson from the schedule.

        Args:
            lesson (Lesson): Lesson to be removed.
        """
        self.lessons.pop(index)

    def save_to_txt_file(self, filename: str) -> None:
        """
        Saves the schedule to a TXT file.
        
        Args:
            filename (str): Name of the file to save the schedule to.
        """
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    def rename(self, new_name: str):
        """
        Renames the schedule.
        
        Args:
            new_name (str): Name to replace the old name of the schedule.
        """
        self.name = new_name
