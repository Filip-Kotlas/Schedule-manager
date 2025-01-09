import tkinter as tk
import math
from typing import Tuple
from PIL import Image, ImageDraw, ImageTk, ImageFont
from app.utils import config
from app.utils import utilities
from app.src.lesson import Lesson
from app.src.schedule import Schedule


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

        hours_in_day = int(self.settings["day_end"][:2])*60 \
                       + int(self.settings["day_end"][3:5]) \
                       - int(self.settings["day_start"][:2])*60 \
                       - int(self.settings["day_start"][3:5])
        hours_in_day = hours_in_day / 60
        # TODO: Zkontrolovat jestli se takto píšou příkazy na více řádků.

        valid_lessons = (lssn for lssn in self.active_schedule.lessons if self.settings["days_in_week"][lssn.day.value] == "1" )
        for lesson in valid_lessons:
            time_delta = lesson.start_time.hour * 60 \
                         + lesson.start_time.minute \
                         - int(self.settings["day_start"][:2])*60 \
                         - int(self.settings["day_start"][3:5])
            days_before = sum((int(char) for char in self.settings["days_in_week"][:lesson.day.value]))

            duration = lesson.end_time.hour*60 + lesson.end_time.minute - lesson.start_time.hour*60 - lesson.start_time.minute
            lesson_width = int(cell_dimension[0]*duration/60)

            x_offset = time_delta / 60 * cell_dimension[0]
            y_offset = days_before * cell_dimension[1]

            if x_offset + lesson_width > 0 and x_offset < hours_in_day * cell_dimension[0]:
                if x_offset < 0:
                    lesson_width = lesson_width + x_offset
                    x_offset = 0
                elif x_offset + lesson_width > hours_in_day * cell_dimension[0]:
                    lesson_width = hours_in_day * cell_dimension[0] - x_offset
                self.draw_lesson_horizontal(draw,
                                            lesson,
                                            base_origin[0] + x_offset,
                                            base_origin[1] + y_offset,
                                            lesson_width,
                                            cell_dimension[1])

    def draw_horizontal_background(self, draw: ImageDraw.ImageDraw) -> Tuple[Tuple[int, int], Tuple[float, float]]:
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        line_width = int(general_size * config.BG_LINE_WIDTH_FACTOR)
        text_size = int(general_size * config.BG_TEXT_SIZE_FACTOR * self.settings["text_scale"])
        text_padding = int(general_size * config.BG_TEXT_PADDING_FACTOR * self.settings["text_scale"])
        schedule_padding = int(general_size * config.BG_SCHEDULE_PADDING_FACTOR)
        side_offset = int(general_size * config.BG_SIDE_OFFSET_FACTOR)
        left_side_offset = int(general_size * config.BG_LEFT_SIDE_OFFSET_FACTOR)

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

    def draw_lesson_horizontal(self, draw: ImageDraw.ImageDraw, lesson: Lesson, x: int, y: int, width: int, height: int) -> None:
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        darker_color = tuple(int(component*config.COLOR_DARKENING_FACTOR) for component in lesson.color)
        outline_width = int(general_size * config.LSSN_OUTLINE_WIDTH_FACTOR)

        draw.rectangle([x, y, x + width, y + height],
                       fill=lesson.color,
                       outline=darker_color,
                       width=outline_width)
        draw.rectangle([x, y + config.LSSN_UPPER_PART_RATIO*height, x + width, y + height],
                       fill="white",
                       outline=lesson.color,
                       width=outline_width)
        draw.line([x+outline_width,
                   y + config.LSSN_UPPER_PART_RATIO*height + (outline_width-1)//2,
                   x + width - outline_width,
                   y + config.LSSN_UPPER_PART_RATIO*height + (outline_width-1)//2],
                  fill="white",
                  width=outline_width)

        text_size = int(height*config.LSSN_UPPER_PART_RATIO*config.LSSN_NAME_TEXT_RATIO)
        text_padding = int(general_size*config.LSSN_TEXT_PADDING_FACTOR)
        text_outline_width = int(max(text_size*config.LSSN_TEXT_OUTLINE_WIDTH_FACTOR, 1))
        text_font = ImageFont.truetype(self.font, max(text_size, 1))
        while text_font.getlength(lesson.name) > width - 2*outline_width - 2*text_padding and text_size > 1:
            text_size -= 1
            text_font = ImageFont.truetype(self.font, text_size)
        # TODO: Změnit velikost textu, aby byla závislá na dostupném místě (a to i šířce).
        # TODO: Umožnit volbu fontu
        mid_x = x + width/2
        mid_y = y + config.LSSN_UPPER_PART_RATIO*height/2
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
        text_size = int(height*(1-config.LSSN_UPPER_PART_RATIO)*config.LSSN_INFO_TEXT_RATIO)
        text_font = ImageFont.truetype(self.font, max(1, text_size))
        while text_font.getlength(lesson.instructor + "  " + lesson.place) > width - 2*outline_width - 2*text_padding and text_size > 1:
            text_size -= 1
            text_font = ImageFont.truetype(self.font, text_size)
        draw.text((x + outline_width + text_padding,
                   y + (1 + config.LSSN_UPPER_PART_RATIO)/2*height - outline_width/2),
                   text=lesson.instructor,
                   font=text_font,
                   fill="black",
                   anchor="lm")
        draw.text((x + width - outline_width - text_padding,
                   y + (1 + config.LSSN_UPPER_PART_RATIO)/2*height - outline_width/2),
                   text=lesson.place,
                   font=text_font,
                   fill="black",
                   anchor="rm")

    def draw_vertical(self, draw: ImageDraw.ImageDraw) -> None:
        base_origin, cell_dimension = self.draw_vertical_background(draw)

        hours_in_day = int(self.settings["day_end"][:2])*60 \
                       + int(self.settings["day_end"][3:5]) \
                       - int(self.settings["day_start"][:2])*60 \
                       - int(self.settings["day_start"][3:5])
        hours_in_day = hours_in_day / 60

        valid_lessons = (lssn for lssn in self.active_schedule.lessons if self.settings["days_in_week"][lssn.day.value] == "1" )
        for lesson in valid_lessons:
            time_delta = lesson.start_time.hour * 60 \
                        + lesson.start_time.minute \
                        - int(self.settings["day_start"][:2])*60 \
                        - int(self.settings["day_start"][3:5])
            days_before = sum((int(char) for char in self.settings["days_in_week"][:lesson.day.value]))

            duration = lesson.end_time.hour * 60 + lesson.end_time.minute - lesson.start_time.hour * 60 - lesson.start_time.minute
            lesson_height = int(cell_dimension[1]*duration/60.0)

            x_offset = days_before * cell_dimension[0]
            y_offset = int(time_delta / 60 * cell_dimension[1])
            if y_offset + lesson_height > 0 and y_offset < hours_in_day * cell_dimension[1]:
                if y_offset < 0:
                    lesson_height = lesson_height + y_offset
                    y_offset = 0
                elif y_offset + lesson_height > hours_in_day * cell_dimension[1]:
                    lesson_height = hours_in_day * cell_dimension[1] - y_offset
                self.draw_lesson_vertical(draw,
                                          lesson,
                                          base_origin[0] + x_offset,
                                          base_origin[1] + y_offset,
                                          cell_dimension[0],
                                          lesson_height)

    def draw_vertical_background(self, draw: ImageDraw.ImageDraw) -> Tuple[Tuple[int, int], Tuple[float, float]]:
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        line_width = int(general_size * config.BG_LINE_WIDTH_FACTOR)
        text_size = int(general_size * config.BG_TEXT_SIZE_FACTOR * self.settings["text_scale"])
        text_padding = int(general_size * config.BG_TEXT_PADDING_FACTOR * self.settings["text_scale"])
        schedule_padding = int(general_size * config.BG_SCHEDULE_PADDING_FACTOR)
        side_offset = int(general_size * config.BG_SIDE_OFFSET_FACTOR)
        top_side_offset = int(general_size * config.BG_TOP_SIDE_OFFSET_FACTOR)

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

    def draw_lesson_vertical(self, draw: ImageDraw.ImageDraw, lesson: Lesson, x: int, y: int, width: int, height: int) -> None:
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        darker_color = tuple(int(component*config.COLOR_DARKENING_FACTOR) for component in lesson.color)
        outline_width = int(general_size * config.LSSN_OUTLINE_WIDTH_FACTOR)

        draw.rectangle([x, y, x + width, y + height],
                       fill=lesson.color,
                       outline=darker_color,
                       width=outline_width)
        draw.rectangle([x, y + config.LSSN_UPPER_PART_RATIO*height, x + width, y + height],
                       fill="white",
                       outline=lesson.color,
                       width=outline_width)
        draw.line([x+outline_width,
                   y + config.LSSN_UPPER_PART_RATIO*height + (outline_width-1)//2,
                   x + width - outline_width,
                   y + config.LSSN_UPPER_PART_RATIO*height + (outline_width-1)//2],
                  fill="white",
                  width=outline_width)

        text_size = int(width*config.LSSN_UPPER_PART_RATIO*config.LSSN_NAME_TEXT_RATIO)
        text_padding = int(general_size*config.LSSN_TEXT_PADDING_FACTOR)
        text_outline_width = int(max(text_size*config.LSSN_TEXT_OUTLINE_WIDTH_FACTOR, 1))
        text_font = ImageFont.truetype(self.font, max(1, text_size))
        while text_font.getlength(lesson.name) > width - 2*outline_width - 2*text_padding and text_size > 1:
            text_size -= 1
            text_font = ImageFont.truetype(self.font, text_size)

        mid_x = x + width/2
        mid_y = y + config.LSSN_UPPER_PART_RATIO*height/2
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
        text_size = int((height*(1-config.LSSN_UPPER_PART_RATIO)-text_padding)/2*config.LSSN_INFO_TEXT_RATIO)
        text_font = ImageFont.truetype(self.font, max(text_size, 1))
        while (text_font.getlength(lesson.instructor) > width - 2*outline_width - 2*text_padding
               or text_font.getlength(lesson.place) > width - 2*outline_width - 2*text_padding
               and text_size > 1):
            text_size -= 1
            text_font = ImageFont.truetype(self.font, text_size)
        draw.text((x + width/2,
                   y + (2/3 * config.LSSN_UPPER_PART_RATIO + 1/3)*height - outline_width/3),
                   text=lesson.instructor,
                   font=text_font,
                   fill="black",
                   anchor="mm")
        draw.text((x + width/2,
                   y + (1/3 * config.LSSN_UPPER_PART_RATIO + 2/3)*height - outline_width/3),
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
