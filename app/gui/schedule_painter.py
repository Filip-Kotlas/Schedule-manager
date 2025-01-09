import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
from typing import Tuple
from datetime import time
from app.utils import config
from app.utils import utilities
from app.src.lesson import Lesson
from app.src.schedule import Schedule
from pathlib import Path
import math


class SchedulePainter():

    def __init__(self):
        self.settings = utilities.load_settings()
        self.image = Image.new("RGB", (self.settings["schedule_width"], self.settings["schedule_height"]), "white")
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.orientation = self.settings["schedule_orientation"]
        self.font = self.settings["text_font"]
        self.bold_font = self.settings["text_bold_font"]
        self.active_schedule = None

    def update(self) -> None:
        self.settings = utilities.load_settings()
        self.image = Image.new("RGB", (self.settings["schedule_width"], self.settings["schedule_height"]), "white")
        self.orientation = self.settings["schedule_orientation"]
        self.font = self.settings["text_font"]
        self.bold_font = self.settings["text_bold_font"]

    def change_schedule(self, schedule: Schedule) -> None:
        self.active_schedule = schedule
        # TODO: Možná přidat kontrolu typu. A to i jinde.

    def draw(self) -> None:
        draw = ImageDraw.Draw(self.image)
        draw.rectangle((0, 0, self.settings["schedule_width"], self.settings["schedule_height"]), fill="white")

        if self.orientation == "horizontal":
            self.draw_horizontal(draw)
        elif self.orientation == "vertical":
            self.draw_vertical(draw)
        else:
            print("Error: Wrong orientation")
            # TODO: Raise exception.

    def draw_horizontal(self, draw: ImageDraw.ImageDraw) -> None:
        base_origin, cell_dimension = self.draw_horizontal_background(draw)

        for lesson in self.active_schedule.lessons:
            time_delta = lesson.start_time.hour * 60 \
                        + lesson.start_time.minute \
                        - int(self.settings["day_start"][:2])*60 \
                        - int(self.settings["day_start"][3:5])
            days_before = sum((int(char) for char in self.settings["days_in_week"][:lesson.day.value]))

            x_offset = int(time_delta / 60 * cell_dimension[0])
            y_offset = days_before * cell_dimension[1]
            self.draw_lesson_horizontal(draw,
                                        lesson,
                                        base_origin[0] + x_offset,
                                        base_origin[1] + y_offset,
                                        cell_dimension[0],
                                        cell_dimension[1])
        # TODO: Finish

    def draw_horizontal_background(self, draw: ImageDraw.ImageDraw) -> Tuple[Tuple[int, int], Tuple[float, float]]:
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        line_width = int(general_size * config.bg_line_width_factor)
        text_size = int(general_size * config.bg_text_size_factor * self.settings["text_scale"])
        text_padding = int(general_size * config.bg_text_padding_factor * self.settings["text_scale"])
        schedule_padding = int(general_size * config.schedule_padding_factor)
        side_offset = int(general_size * config.side_offset_factor)
        left_side_offset = int(general_size * config.left_side_offset_factor)

        start_hour = int(self.settings["day_start"][0:2])
        end_hour = int(self.settings["day_end"][0:2])
        if end_hour <= start_hour:
            end_hour += 24
        column_number = end_hour - start_hour
        row_number = self.settings["days_in_week"].count("1")
        #TODO: Přidat vyjímku

        cell_width = (self.settings["schedule_width"] - 2*schedule_padding - left_side_offset - side_offset) / float(column_number)
        cell_height = (self.settings["schedule_height"] - 2*schedule_padding - text_size - text_padding - 2*side_offset) / float(row_number)
        base_origin = (schedule_padding + left_side_offset,
                       schedule_padding + text_size + text_padding + side_offset)

        text_font = ImageFont.truetype(self.bold_font, text_size)
        draw.text((schedule_padding, schedule_padding), text=self.active_schedule.name, fill="black", font=text_font, anchor="lt")
        text_font = ImageFont.truetype(self.font, text_size)

        increment = 0
        for hour in (f"{i%24}:00" for i in range(start_hour, end_hour + 1)):
            x1 = schedule_padding + left_side_offset + increment*cell_width
            y1 = schedule_padding + text_size + text_padding
            x2 = x1
            y2 = self.settings["schedule_height"] - schedule_padding
            draw.line((x1, y1, x2, y2), fill="lightgrey", width=line_width)
            draw.text((x1, schedule_padding + text_size/2), text=hour, fill="black", font=text_font, anchor="mm")
            increment += 1

        days_in_week = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
        selected_days = (day for char, day in zip(self.settings["days_in_week"], days_in_week) if char == "1")
        increment = 0
        for day in selected_days:
            x1 = schedule_padding
            y1 = schedule_padding + text_size + text_padding + side_offset + increment*cell_height
            x2 = self.settings["schedule_width"] - schedule_padding
            y2 = y1
            draw.line((x1, y1, x2, y2), fill="lightgrey", width=line_width)
            draw.text((x1, y1 + cell_height/2), text=day, fill="black", font=text_font, anchor="lm")
            increment += 1
        y1 = schedule_padding + text_size + text_padding + side_offset + increment*cell_height
        y2 = y1
        draw.line((x1, y1, x2, y2), fill="lightgrey", width=line_width)

        return (base_origin, (cell_width, cell_height))

    def draw_lesson_horizontal(self, draw: ImageDraw.ImageDraw, lesson: Lesson, x: int, y: int, hour_width: int, day_height: int) -> None:
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        darker_color = tuple(int(component*config.color_darkening_factor) for component in lesson.color)
        duration = lesson.end_time.hour * 60 + lesson.end_time.minute - lesson.start_time.hour * 60 - lesson.start_time.minute
        outline_width = int(general_size * config.lssn_outline_width_factor)

        draw.rectangle([x, y, x + hour_width*duration/60.0, y + day_height],
                       fill=lesson.color,
                       outline=darker_color,
                       width=outline_width)
        draw.rectangle([x, y + config.lssn_upper_part_ratio*day_height, x + hour_width*duration/60.0, y + day_height],
                       fill="white",
                       outline=lesson.color,
                       width=outline_width)
        draw.line([x+outline_width,
                   y + config.lssn_upper_part_ratio*day_height + (outline_width-1)//2,
                   x + hour_width*duration/60.0 - outline_width,
                   y + config.lssn_upper_part_ratio*day_height + (outline_width-1)//2],
                  fill="white",
                  width=outline_width)

        text_size = int(day_height*config.lssn_upper_part_ratio*config.lssn_name_text_ratio)
        text_padding = int(general_size*config.lssn_text_padding_factor)
        text_outline_width = int(max(text_size*config.lssn_text_outline_width_factor, 1))
        text_font = ImageFont.truetype(self.font, text_size)
        while text_font.getlength(lesson.name) > hour_width*duration/60.0 - 2*outline_width - 2*text_padding:
            text_size -= 1
            text_font = ImageFont.truetype(self.font, text_size)
        # TODO: Změnit velikost textu, aby byla závislá na dostupném místě (a to i šířce).
        # TODO: Umožnit volbu fontu
        mid_x = x + hour_width*duration/60.0/2
        mid_y = y + config.lssn_upper_part_ratio*day_height/2
        for dx in range(-text_outline_width, text_outline_width + 1):
            for dy in range(-text_outline_width, text_outline_width + 1):
                draw.text((mid_x + dx, mid_y + dy),
                          lesson.name,
                          fill="white",
                          font=text_font,
                          anchor="mm")
        draw.text((mid_x, mid_y),
                  lesson.name,
                  fill="black",
                  font=text_font,
                  anchor="mm")
        text_size = int(day_height*(1-config.lssn_upper_part_ratio)*config.lssn_info_text_ratio)
        text_font = ImageFont.truetype(self.font, text_size)
        while text_font.getlength(lesson.instructor + "  " + lesson.place) > hour_width*duration/60.0 - 2*outline_width - 2*text_padding:
            text_size -= 1
            text_font = ImageFont.truetype(self.font, text_size)
        draw.text((x + outline_width + text_padding,
                   y + (1 + config.lssn_upper_part_ratio)/2*day_height - outline_width/2),
                   text=lesson.instructor,
                   font=text_font,
                   fill="black",
                   anchor="lm")
        draw.text((x + hour_width*duration/60.0 - outline_width - text_padding,
                   y + (1 + config.lssn_upper_part_ratio)/2*day_height - outline_width/2),
                   text=lesson.place,
                   font=text_font,
                   fill="black",
                   anchor="rm")

    def draw_vertical(self, draw: ImageDraw.ImageDraw) -> None:
        base_origin, cell_dimension = self.draw_vertical_background(draw)

        for lesson in self.active_schedule.lessons:
            time_delta = lesson.start_time.hour * 60 \
                        + lesson.start_time.minute \
                        - int(self.settings["day_start"][:2])*60 \
                        - int(self.settings["day_start"][3:5])
            days_before = sum((int(char) for char in self.settings["days_in_week"][:lesson.day.value]))

            x_offset = days_before * cell_dimension[0]
            y_offset = int(time_delta / 60 * cell_dimension[1])
            self.draw_lesson_vertical(draw,
                                        lesson,
                                        base_origin[0] + x_offset,
                                        base_origin[1] + y_offset,
                                        cell_dimension[0],
                                        cell_dimension[1])

    def draw_vertical_background(self, draw: ImageDraw.ImageDraw) -> Tuple[Tuple[int, int], Tuple[float, float]]:
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        line_width = int(general_size * config.bg_line_width_factor)
        text_size = int(general_size * config.bg_text_size_factor * self.settings["text_scale"])
        text_padding = int(general_size * config.bg_text_padding_factor * self.settings["text_scale"])
        schedule_padding = int(general_size * config.schedule_padding_factor)
        side_offset = int(general_size * config.side_offset_factor)
        top_side_offset = int(general_size * config.top_side_offset_factor)

        start_hour = int(self.settings["day_start"][0:2])
        end_hour = int(self.settings["day_end"][0:2])
        if end_hour <= start_hour:
            end_hour += 24
        row_number = end_hour - start_hour
        column_number = self.settings["days_in_week"].count("1")
        #TODO: Přidat vyjímku

        text_font = ImageFont.truetype(self.bold_font, text_size)
        draw.text((schedule_padding, schedule_padding), text=self.active_schedule.name, fill="black", font=text_font, anchor="lt")
        text_font = ImageFont.truetype(self.font, text_size)

        times = [f"{i%24}:00" for i in range(start_hour, end_hour + 1)]
        time_text_length = max((text_font.getlength(time) for time in times))

        cell_width = (self.settings["schedule_width"]
                      - 2*schedule_padding
                      - time_text_length
                      - text_padding
                      - 2*side_offset) / float(column_number)
        cell_height = (self.settings["schedule_height"]
                       - 2*schedule_padding
                       - text_size
                       - text_padding
                       - top_side_offset
                       - side_offset) / float(row_number)
        # TODO: Okomentovat, co to znamená
        base_origin = (schedule_padding + time_text_length + text_padding + side_offset,
                       schedule_padding + top_side_offset + text_size + text_padding)

        increment = 0
        for hour in times:
            x1 = schedule_padding + time_text_length + text_padding
            y1 = schedule_padding + top_side_offset + text_size + text_padding + increment*cell_height
            x2 = self.settings["schedule_width"] - schedule_padding
            y2 = y1
            draw.line((x1, y1, x2, y2), fill="lightgrey", width=line_width)
            draw.text((schedule_padding + time_text_length/2, y1), text=hour, fill="black", font=text_font, anchor="mm")
            increment += 1

        days_in_week = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
        selected_days = (day for char, day in zip(self.settings["days_in_week"], days_in_week) if char == "1")
        increment = 0
        for day in selected_days:
            x1 = schedule_padding + time_text_length + text_padding + side_offset + increment*cell_width
            y1 = schedule_padding
            x2 = x1
            y2 = self.settings["schedule_height"] - schedule_padding
            draw.line((x1, y1, x2, y2), fill="lightgrey", width=line_width)
            draw.text((x1 + cell_width/2, y1 + top_side_offset + text_size/2), text=day, fill="black", font=text_font, anchor="mm")
            increment += 1
        x1 = schedule_padding + time_text_length + text_padding + side_offset + increment*cell_width
        x2 = x1
        draw.line((x1, y1, x2, y2), fill="lightgrey", width=line_width)

        return (base_origin, (cell_width, cell_height))

    def draw_lesson_vertical(self, draw: ImageDraw.ImageDraw, lesson: Lesson, x: int, y: int, day_width: int, hour_height: int) -> None:
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        darker_color = tuple(int(component*config.color_darkening_factor) for component in lesson.color)
        duration = lesson.end_time.hour * 60 + lesson.end_time.minute - lesson.start_time.hour * 60 - lesson.start_time.minute
        outline_width = int(general_size * config.lssn_outline_width_factor)

        draw.rectangle([x, y, x + day_width, y + hour_height*duration/60.0],
                       fill=lesson.color,
                       outline=darker_color,
                       width=outline_width)
        draw.rectangle([x, y + config.lssn_upper_part_ratio*hour_height*duration/60.0, x + day_width, y + hour_height*duration/60.0],
                       fill="white",
                       outline=lesson.color,
                       width=outline_width)
        draw.line([x+outline_width,
                   y + config.lssn_upper_part_ratio*hour_height*duration/60.0 + (outline_width-1)//2,
                   x + day_width - outline_width,
                   y + config.lssn_upper_part_ratio*hour_height*duration/60.0 + (outline_width-1)//2],
                  fill="white",
                  width=outline_width)

        text_size = int(day_width*config.lssn_upper_part_ratio*config.lssn_name_text_ratio)
        text_padding = int(general_size*config.lssn_text_padding_factor)
        text_outline_width = int(max(text_size*config.lssn_text_outline_width_factor, 1))
        text_font = ImageFont.truetype(self.font, text_size)
        while text_font.getlength(lesson.name) > day_width - 2*outline_width - 2*text_padding:
            text_size -= 1
            text_font = ImageFont.truetype(self.font, text_size)
        # TODO: Změnit velikost textu, aby byla závislá na dostupném místě (a to i šířce).
        # TODO: Umožnit volbu fontu
        mid_x = x + day_width/2
        mid_y = y + config.lssn_upper_part_ratio*hour_height*duration/60.0/2
        for dx in range(-text_outline_width, text_outline_width + 1):
            for dy in range(-text_outline_width, text_outline_width + 1):
                draw.text((mid_x + dx, mid_y + dy),
                          lesson.name,
                          fill="white",
                          font=text_font,
                          anchor="mm")
        draw.text((mid_x, mid_y),
                  lesson.name,
                  fill="black",
                  font=text_font,
                  anchor="mm")
        text_size = int((hour_height*duration/60.0*(1-config.lssn_upper_part_ratio)-text_padding)/2*config.lssn_info_text_ratio)
        text_font = ImageFont.truetype(self.font, text_size)
        while (text_font.getlength(lesson.instructor) > day_width - 2*outline_width - 2*text_padding
               or text_font.getlength(lesson.place) > day_width - 2*outline_width - 2*text_padding):
            text_size -= 1
            text_font = ImageFont.truetype(self.font, text_size)
        draw.text((x + day_width/2,
                   y + (2/3 * config.lssn_upper_part_ratio + 1/3)*hour_height*duration/60.0 - outline_width/3),
                   text=lesson.instructor,
                   font=text_font,
                   fill="black",
                   anchor="mm")
        draw.text((x + day_width/2,
                   y + (1/3 * config.lssn_upper_part_ratio + 2/3)*hour_height*duration/60.0 - outline_width/3),
                   text=lesson.place,
                   font=text_font,
                   fill="black",
                   anchor="mm")

    def get_canvas(self, parent_widget) -> tk.Canvas:
        canvas = tk.Canvas(parent_widget, width=self.settings["schedule_width"], height=self.settings["schedule_height"], background="red")
        self.tk_image = ImageTk.PhotoImage(self.image)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        return canvas
