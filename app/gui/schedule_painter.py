"""Contains class responsible for drawing the schedule."""
import math
from typing import Tuple
from typing import Dict
from typing import List

from PIL import Image, ImageDraw, ImageFont

from app.utils import config
from app.utils import utilities
from app.src.lesson import Lesson
from app.src.schedule import Schedule


class SchedulePainter():
    """Drawing agent of the schedule."""

    def __init__(self):
        self.settings = utilities.load_settings(config.SETTINGS_PATH)
        self.image = Image.new("RGB",
                               (self.settings["schedule_width"], self.settings["schedule_height"]),
                               "white")
        self.font = self.settings["text_font"]
        self.bold_font = self.settings["text_bold_font"]
        self.active_schedule = None

    def update(self) -> None:
        """Updates the settings of the schedule."""
        self.settings = utilities.load_settings(config.SETTINGS_PATH)
        self.font = self.settings["text_font"]
        self.bold_font = self.settings["text_bold_font"]
        self.update_image()

    def update_image(self) -> None:
        """Updates image of the painter."""
        self.image = Image.new("RGB",
                               (self.settings["schedule_width"], self.settings["schedule_height"]),
                               "white")

    def change_schedule(self, schedule: Schedule) -> None:
        """
        Changes the active schedule.
        
        Args:
            schedule (Schedule): New schedule.
        """
        self.active_schedule = schedule

    def draw(self) -> None:
        """
        Draws the schedule to the image.
        
        Based on the set orientation draws the horizontal or vertical schedule.
        """
        draw = ImageDraw.Draw(self.image)
        draw.rectangle((0, 0, self.settings["schedule_width"], self.settings["schedule_height"]),
                       fill="white")

        if self.settings["schedule_orientation"] == "horizontal":
            self.draw_horizontal(draw)
        elif self.settings["schedule_orientation"] == "vertical":
            self.draw_vertical(draw)
        else:
            raise ValueError

    def draw_horizontal(self, draw: ImageDraw.ImageDraw) -> None:
        """
        Draws the schedule horizontally.

        Draws the background of the schedule. Then draws the lessons of the schedule that take place
        in the days that are set in the settings to be shown. If a lesson, partially or wholly,
        takes place outside of the set times of the schedule, only the part of the lesson that
        protrude into the set times is drawn.

        Args:
            draw (ImageDraw.ImageDraw): Drawing object.
        """
        base_origin, cell_dimension = self.draw_horizontal_background(draw)

        hours_in_day = (int(self.settings["day_end"][:2])*60
                        + int(self.settings["day_end"][3:5])
                        - int(self.settings["day_start"][:2])*60
                        - int(self.settings["day_start"][3:5]))
        hours_in_day = hours_in_day / 60

        valid_lessons = [lssn for lssn in self.active_schedule.lessons if self.settings["days_in_week"][lssn.day.value] == "1"]
        for lesson in valid_lessons:
            try:
                collision_bool = lesson.has_collision(valid_lessons)
            except Exception as e:
                print(f"Chyba: {e}")
                collision_bool = False, False

            lesson_dimensions = [0, 0]
            lesson_dimensions[1] = cell_dimension[1]
            days_before = sum((int(char) for char in self.settings["days_in_week"][:lesson.day.value]))
            y_offset = days_before * cell_dimension[1]
            if collision_bool[0]:
                lesson_dimensions[1] = int(cell_dimension[1]/2)
                if not collision_bool[1]:
                    y_offset += lesson_dimensions[1]

            time_delta = lesson.start_time.hour * 60 \
                         + lesson.start_time.minute \
                         - int(self.settings["day_start"][:2])*60 \
                         - int(self.settings["day_start"][3:5])
            x_offset = time_delta / 60 * cell_dimension[0]

            duration = (lesson.end_time.hour*60
                        + lesson.end_time.minute
                        - lesson.start_time.hour*60
                        - lesson.start_time.minute)
            lesson_dimensions[0] = int(cell_dimension[0]*duration/60)


            if x_offset + lesson_dimensions[0] > 0 and x_offset < hours_in_day * cell_dimension[0]:
                if x_offset < 0:
                    lesson_dimensions[0] = lesson_dimensions[0] + x_offset
                    x_offset = 0
                elif x_offset + lesson_dimensions[0] > hours_in_day * cell_dimension[0]:
                    lesson_dimensions[0] = hours_in_day * cell_dimension[0] - x_offset
                self.draw_lesson_horizontal(draw,
                                            lesson,
                                            (base_origin[0] + x_offset, base_origin[1] + y_offset),
                                            (lesson_dimensions[0], lesson_dimensions[1]))

    def compute_schedule_layout_dimensions(self) -> Dict:
        """
        Computes the dimensions of layout of the background of the schedule.
        
        Returns:
            Dict: The layout dimensions.
        """
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        layout_dimensions = {
            "line_width": int(general_size * config.BG_LINE_WIDTH_FACTOR),
            "text_size": int(general_size * config.BG_TEXT_SIZE_FACTOR * self.settings["text_scale"]),
            "text_padding": int(general_size * config.BG_TEXT_PADDING_FACTOR * self.settings["text_scale"]),
            "schedule_padding": int(general_size * config.BG_SCHEDULE_PADDING_FACTOR),
            "side_offset": int(general_size * config.BG_SIDE_OFFSET_FACTOR),
            "top_side_offset": int(general_size * config.BG_TOP_SIDE_OFFSET_FACTOR),
            "left_side_offset": int(general_size * config.BG_LEFT_SIDE_OFFSET_FACTOR)
        }
        return layout_dimensions

    def draw_horizontal_background(self, draw: ImageDraw.ImageDraw) -> Tuple[Tuple[int, int], Tuple[float, float]]:
        """
        Draws background lines and time and day labels to the horizontal schedule.

        Draws the name of the schedule to the top right-hand corner. Draws vertical lines and
        time labels. Draws horizontal lines with day labels.

        Returns:
            Tuple[Tuple[int, int], Tuple[float, float]]: Tuple of two tuples. The first tuple
                contains coordinates of the origin of the base of the schedule, ie. rectangle where
                the actual lessons are to be drawn. The second tuple contains width and height of
                the cells of the schedule.
        """
        lay_dim = self.compute_schedule_layout_dimensions()

        start_hour = int(self.settings["day_start"][0:2])
        end_hour = int(self.settings["day_end"][0:2])
        if end_hour <= start_hour:
            end_hour += 24
        column_number = end_hour - start_hour

        cell_width = (self.settings["schedule_width"]
                      - 2*lay_dim["schedule_padding"]
                      - lay_dim["left_side_offset"]
                      - lay_dim["side_offset"])/float(column_number)
        cell_height = (self.settings["schedule_height"]
                       - 2*lay_dim["schedule_padding"]
                       - lay_dim["text_size"]
                       - lay_dim["text_padding"]
                       - 2*lay_dim["side_offset"])/float(self.settings["days_in_week"].count("1"))
        base_origin = (lay_dim["schedule_padding"] + lay_dim["left_side_offset"],
                       (lay_dim["schedule_padding"]
                        + lay_dim["text_size"]
                        + lay_dim["text_padding"]
                        + lay_dim["side_offset"]))

        draw.text((lay_dim["schedule_padding"], lay_dim["schedule_padding"]),
                  text=self.active_schedule.name,
                  fill="black",
                  font=ImageFont.truetype(self.bold_font, lay_dim["text_size"]),
                  anchor="lt")

        for increment, hour in enumerate(f"{i%24}:00" for i in range(start_hour, end_hour + 1)):
            coords = [lay_dim["schedule_padding"] + lay_dim["left_side_offset"] + increment*cell_width,
                      lay_dim["schedule_padding"] + lay_dim["text_size"] + lay_dim["text_padding"],
                      lay_dim["schedule_padding"] + lay_dim["left_side_offset"] + increment*cell_width,
                      self.settings["schedule_height"] - lay_dim["schedule_padding"]]
            draw.line(coords, fill="lightgrey", width=lay_dim["line_width"])
            draw.text((coords[0],
                       lay_dim["schedule_padding"] + lay_dim["text_size"]/2),
                       text=hour, fill="black",
                       font=ImageFont.truetype(self.font, lay_dim["text_size"]),
                       anchor="mm")

        days_in_week = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
        selected_days = (day for char, day in zip(self.settings["days_in_week"], days_in_week) if char == "1")
        for increment, day in enumerate(selected_days):
            coords = [lay_dim["schedule_padding"],
                      (lay_dim["schedule_padding"]
                      + lay_dim["text_size"]
                      + lay_dim["text_padding"]
                      + lay_dim["side_offset"]
                      + increment*cell_height),
                      self.settings["schedule_width"] - lay_dim["schedule_padding"],
                      (lay_dim["schedule_padding"]
                      + lay_dim["text_size"]
                      + lay_dim["text_padding"]
                      + lay_dim["side_offset"]
                      + increment*cell_height)]
            draw.line(coords, fill="lightgrey", width=lay_dim["line_width"])
            draw.text((coords[0], coords[1] + cell_height/2),
                      text=day,
                      fill="black",
                      font=ImageFont.truetype(self.font, lay_dim["text_size"]),
                      anchor="lm")
        increment += 1
        coords[1] = (lay_dim["schedule_padding"]
                     + lay_dim["text_size"]
                     + lay_dim["text_padding"]
                     + lay_dim["side_offset"]
                     + increment*cell_height)
        coords[3] = coords[1]
        draw.line(coords, fill="lightgrey", width=lay_dim["line_width"])

        return (base_origin, (cell_width, cell_height))

    def draw_lesson_horizontal(self,
                               draw: ImageDraw.ImageDraw,
                               lesson: Lesson,
                               coordinates: Tuple[int, int],
                               dimensions: Tuple[int, int]) -> None:
        """
        Draws a lesson horizontally on given coordinates with given width and height.

        Args:
            draw (ImageDraw): Agent to be drawn with.
            lesson (Lesson): Lesson to be drawn.
            coordinates (Tuple[int, int]): Coordinates where the upper right corner is to be drawn.
            dimensions (Tuple[int, int]): Width and height of the lesson.
        """
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        lay_dim = {"outline_width": int(general_size * config.LSSN_OUTLINE_WIDTH_FACTOR),
                   "text_size": int(dimensions[1]*config.LSSN_UPPER_PART_RATIO*config.LSSN_NAME_TEXT_RATIO),
                   "text_padding": int(general_size*config.LSSN_TEXT_PADDING_FACTOR)}
        lay_dim["text_outline_width"] = int(max(lay_dim["text_size"]*config.LSSN_TEXT_OUTLINE_WIDTH_FACTOR, 1))

        darker_color = tuple(int(component*config.COLOR_DARKENING_FACTOR) for component in lesson.color)
        draw.rectangle([coordinates[0], coordinates[1], coordinates[0] + dimensions[0], coordinates[1] + dimensions[1]],
                       fill=lesson.color,
                       outline=darker_color,
                       width=lay_dim["outline_width"])
        draw.rectangle([coordinates[0], coordinates[1] + config.LSSN_UPPER_PART_RATIO*dimensions[1], coordinates[0] + dimensions[0], coordinates[1] + dimensions[1]],
                       fill="white",
                       outline=lesson.color,
                       width=lay_dim["outline_width"])
        draw.line([coordinates[0]+lay_dim["outline_width"],
                   coordinates[1] + config.LSSN_UPPER_PART_RATIO*dimensions[1] + (lay_dim["outline_width"]-1)//2,
                   coordinates[0] + dimensions[0] - lay_dim["outline_width"],
                   coordinates[1] + config.LSSN_UPPER_PART_RATIO*dimensions[1] + (lay_dim["outline_width"]-1)//2],
                  fill="white",
                  width=lay_dim["outline_width"])

        text_font = ImageFont.truetype(self.font, max(lay_dim["text_size"], 1))
        while text_font.getlength(lesson.name) > dimensions[0] - 2*lay_dim["outline_width"] - 2*lay_dim["text_padding"] and lay_dim["text_size"] > 1:
            lay_dim["text_size"] -= 1
            text_font = ImageFont.truetype(self.font, lay_dim["text_size"])

        mid_x = coordinates[0] + dimensions[0]/2
        mid_y = coordinates[1] + config.LSSN_UPPER_PART_RATIO*dimensions[1]/2
        for dx in range(-lay_dim["text_outline_width"], lay_dim["text_outline_width"] + 1):
            for dy in range(-lay_dim["text_outline_width"], lay_dim["text_outline_width"] + 1):
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
        lay_dim["text_size"] = int(dimensions[1]*(1-config.LSSN_UPPER_PART_RATIO)*config.LSSN_INFO_TEXT_RATIO)
        text_font = ImageFont.truetype(self.font, max(1, lay_dim["text_size"]))
        while text_font.getlength(lesson.instructor + "  " + lesson.place) > dimensions[0] - 2*lay_dim["outline_width"] - 2*lay_dim["text_padding"] and lay_dim["text_size"] > 1:
            lay_dim["text_size"] -= 1
            text_font = ImageFont.truetype(self.font, lay_dim["text_size"])
        draw.text((coordinates[0] + lay_dim["outline_width"] + lay_dim["text_padding"],
                   coordinates[1] + (1 + config.LSSN_UPPER_PART_RATIO)/2*dimensions[1] - lay_dim["outline_width"]/2),
                   text=lesson.instructor,
                   font=text_font,
                   fill="black",
                   anchor="lm")
        draw.text((coordinates[0] + dimensions[0] - lay_dim["outline_width"] - lay_dim["text_padding"],
                   coordinates[1] + (1 + config.LSSN_UPPER_PART_RATIO)/2*dimensions[1] - lay_dim["outline_width"]/2),
                   text=lesson.place,
                   font=text_font,
                   fill="black",
                   anchor="rm")

    def draw_vertical(self, draw: ImageDraw.ImageDraw) -> None:
        """
        Draws the schedule vertically.

        Draws the background of the schedule. Then draws the lessons of the schedule that take place
        in the days that are set in the settings to be shown. If a lesson, partially or wholly,
        takes place outside of the set times of the schedule, only the part of the lesson that
        protrude into the set times is drawn.

        Args:
            draw (ImageDraw.ImageDraw): Drawing object.
        """
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
                                          (base_origin[0] + x_offset, base_origin[1] + y_offset),
                                          (cell_dimension[0], lesson_height))

    def draw_vertical_background(self, draw: ImageDraw.ImageDraw) -> Tuple[Tuple[int, int], Tuple[float, float]]:
        """
        Draws background lines and time and day labels of the vertical schedule.

        Draws the name of the schedule to the top right-hand corner. Then draws horizontal lines and
        time labels. Finally it draws vertical lines and day labels.

        Returns:
            Tuple[Tuple[int, int], Tuple[float, float]]: Tuple of two tuples. The first tuple
                contains coordinates of the origin of the base of the schedule, ie. rectangle where
                the actual lessons are to be drawn. The second tuple contains width and height of
                the cells of the schedule.
        """
        lay_dim = self.compute_schedule_layout_dimensions()

        start_hour = int(self.settings["day_start"][0:2])
        end_hour = int(self.settings["day_end"][0:2])
        if end_hour <= start_hour:
            end_hour += 24

        draw.text((lay_dim["schedule_padding"], lay_dim["schedule_padding"]),
                  text=self.active_schedule.name,
                  fill="black",
                  font=ImageFont.truetype(self.bold_font, lay_dim["text_size"]),
                  anchor="lt")

        times = [f"{i%24}:00" for i in range(start_hour, end_hour + 1)]
        time_text_length = max((ImageFont.truetype(self.font, lay_dim["text_size"]).getlength(time) for time in times))

        cell_width = (self.settings["schedule_width"]
                      - 2*lay_dim["schedule_padding"]
                      - time_text_length
                      - lay_dim["text_padding"]
                      - 2*lay_dim["side_offset"])/float(self.settings["days_in_week"].count("1"))
        cell_height = (self.settings["schedule_height"]
                       - 2*lay_dim["schedule_padding"]
                       - lay_dim["text_size"]
                       - lay_dim["text_padding"]
                       - lay_dim["top_side_offset"]
                       - lay_dim["side_offset"])/float(end_hour - start_hour)
        base_origin = (lay_dim["schedule_padding"] + time_text_length + lay_dim["text_padding"] + lay_dim["side_offset"],
                       lay_dim["schedule_padding"] + lay_dim["top_side_offset"] + lay_dim["text_size"] + lay_dim["text_padding"])

        for increment, hour in enumerate(times):
            coords = [lay_dim["schedule_padding"] + time_text_length + lay_dim["text_padding"],
                      (lay_dim["schedule_padding"]
                       + lay_dim["top_side_offset"]
                       + lay_dim["text_size"]
                       + lay_dim["text_padding"]
                       + increment*cell_height),
                       self.settings["schedule_width"] - lay_dim["schedule_padding"],
                       (lay_dim["schedule_padding"]
                       + lay_dim["top_side_offset"]
                       + lay_dim["text_size"]
                       + lay_dim["text_padding"]
                       + increment*cell_height)]
            draw.line(coords, fill="lightgrey", width=lay_dim["line_width"])
            draw.text((lay_dim["schedule_padding"] + time_text_length/2, coords[1]),
                      text=hour,
                      fill="black",
                      font=ImageFont.truetype(self.font, lay_dim["text_size"]),
                      anchor="mm")

        days_in_week = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
        for increment, day in enumerate((day for char, day in zip(self.settings["days_in_week"], days_in_week) if char == "1")):
            coords = [(lay_dim["schedule_padding"]
                       + time_text_length
                       + lay_dim["text_padding"]
                       + lay_dim["side_offset"]
                       + increment*cell_width),
                      lay_dim["schedule_padding"],
                      (lay_dim["schedule_padding"]
                       + time_text_length
                       + lay_dim["text_padding"]
                       + lay_dim["side_offset"]
                       + increment*cell_width),
                      self.settings["schedule_height"] - lay_dim["schedule_padding"]]
            draw.line(coords, fill="lightgrey", width=lay_dim["line_width"])
            draw.text((coords[0] + cell_width/2, coords[1] + lay_dim["top_side_offset"] + lay_dim["text_size"]/2),
                      text=day,
                      fill="black",
                      font=ImageFont.truetype(self.font, lay_dim["text_size"]),
                      anchor="mm")
        increment += 1
        coords[0] = lay_dim["schedule_padding"] + time_text_length + lay_dim["text_padding"] + lay_dim["side_offset"] + increment*cell_width
        coords[2] = coords[0]
        draw.line(coords, fill="lightgrey", width=lay_dim["line_width"])

        return (base_origin, (cell_width, cell_height))

    def draw_lesson_vertical(self, draw: ImageDraw.ImageDraw, lesson: Lesson, coord: Tuple[int, int], dim: Tuple[int, int]) -> None:
        """
        Draws a lesson vertically on given coordinates with given width and height.

        Args:
            draw (ImageDraw): Agent to be drawn with.
            lesson (Lesson): Lesson to be drawn.
            coordinates (Tuple[int, int]): Coordinates where the upper right corner is to be drawn.
            dimensions (Tuple[int, int]): Width and height of the lesson.
        """
        general_size = int(math.sqrt(self.settings["schedule_height"]**2 + self.settings["schedule_width"]**2))
        lay_dim = {"outline_width": int(general_size * config.LSSN_OUTLINE_WIDTH_FACTOR),
                   "text_size": int(dim[0]*config.LSSN_UPPER_PART_RATIO*config.LSSN_NAME_TEXT_RATIO),
                   "text_padding": int(general_size*config.LSSN_TEXT_PADDING_FACTOR)}
        lay_dim["text_outline_width"] = int(max(lay_dim["text_size"]*config.LSSN_TEXT_OUTLINE_WIDTH_FACTOR, 1))

        darker_color = tuple(int(component*config.COLOR_DARKENING_FACTOR) for component in lesson.color)
        draw.rectangle([coord[0], coord[1], coord[0] + dim[0], coord[1] + dim[1]],
                       fill=lesson.color,
                       outline=darker_color,
                       width=lay_dim["outline_width"])
        draw.rectangle([coord[0], coord[1] + config.LSSN_UPPER_PART_RATIO*dim[1], coord[0] + dim[0], coord[1] + dim[1]],
                       fill="white",
                       outline=lesson.color,
                       width=lay_dim["outline_width"])
        draw.line([coord[0] + lay_dim["outline_width"],
                   coord[1] + config.LSSN_UPPER_PART_RATIO*dim[1] + (lay_dim["outline_width"]-1)//2,
                   coord[0] + dim[0] - lay_dim["outline_width"],
                   coord[1] + config.LSSN_UPPER_PART_RATIO*dim[1] + (lay_dim["outline_width"]-1)//2],
                  fill="white",
                  width=lay_dim["outline_width"])

        text_font = ImageFont.truetype(self.font, max(1, lay_dim["text_size"]))
        while text_font.getlength(lesson.name) > dim[0] - 2*lay_dim["outline_width"] - 2*lay_dim["text_padding"] and lay_dim["text_size"] > 1:
            lay_dim["text_size"] -= 1
            text_font = ImageFont.truetype(self.font, lay_dim["text_size"])

        mid_x = coord[0] + dim[0]/2
        mid_y = coord[1] + config.LSSN_UPPER_PART_RATIO*dim[1]/2
        for dx in range(-lay_dim["text_outline_width"], lay_dim["text_outline_width"] + 1):
            for dy in range(-lay_dim["text_outline_width"], lay_dim["text_outline_width"] + 1):
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
        lay_dim["text_size"] = int((dim[1]*(1-config.LSSN_UPPER_PART_RATIO)-lay_dim["text_padding"])/2*config.LSSN_INFO_TEXT_RATIO)
        text_font = ImageFont.truetype(self.font, max(lay_dim["text_size"], 1))
        while (text_font.getlength(lesson.instructor) > dim[0] - 2*lay_dim["outline_width"] - 2*lay_dim["text_padding"]
               or text_font.getlength(lesson.place) > dim[0] - 2*lay_dim["outline_width"] - 2*lay_dim["text_padding"]
               and lay_dim["text_size"] > 1):
            lay_dim["text_size"] -= 1
            text_font = ImageFont.truetype(self.font, lay_dim["text_size"])
        draw.text((coord[0] + dim[0]/2,
                   coord[1] + (2/3 * config.LSSN_UPPER_PART_RATIO + 1/3)*dim[1] - lay_dim["outline_width"]/3),
                   text=lesson.instructor,
                   font=text_font,
                   fill="black",
                   anchor="mm")
        draw.text((coord[0] + dim[0]/2,
                   coord[1] + (1/3 * config.LSSN_UPPER_PART_RATIO + 2/3)*dim[1] - lay_dim["outline_width"]/3),
                   text=lesson.place,
                   font=text_font,
                   fill="black",
                   anchor="mm")

    def get_image(self) -> Image:
        """
        Returns image of the schedule.

        Returns:
            (Image): Image to be returned.
        """
        return self.image
