# Built in modules
from bidi.algorithm import get_display
from typing import Tuple, List, Optional
import math
import os
import random
import logging

# Pillow
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Mathplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as font_manager
import pylab

# My code
from translator import StringManager

logger = logging.getLogger(__name__)


class ImageGenerator:

    BACKGROUND_COLORS = {
        0:      (105, 191, 226),
        100:    (105, 226, 185),
        250:    (111, 226, 105),
        500:    (168, 226, 105),
        1_000:  (246, 171, 65),
        2_500:  (246, 120, 65),
        5_000:  (246, 65,  65),
        10_000: (140, 29,  20),
    }

    ASSETS_FOLDER = os.path.join("assets")
    RANDOM_BACKGROUND_IMAGES_FOLDER = os.path.join(
        ASSETS_FOLDER, "backgrounds")

    # - - - T I T L E S - A N D - V A L U E S - - - #

    # Colors
    TITLE_COLOR = (255, 255, 255)
    VALUE_COLOR = (255, 255, 255)
    SUBTITLE_COLOR = (255, 255, 255)
    FIG_COLOR = (255, 255, 255)
    BOTTOM_TEXT_COLOR = (255, 255, 255)

    # Font sizes
    BIG_TITLE_SIZE = 200
    BIG_VALUE_SIZE = 300
    SMALL_TITLE_SIZE = 100
    SMALL_VALUE_SIZE = 150
    SMALL_SUBTITLE_SIZE = 75
    BOTTOM_TEXT_SIZE = 25

    # Padding
    PADDING_BETWEEN_BIG_TITLE_AND_VALUE = 135
    PADDING_BETWEEN_SMALL_TITLE_AND_VALUE = 75
    PADDING_BETWEEN_SMALL_VALUE_AND_SUBTITLE = 150
    SMALL_TITLES_SIDE_PADDING = 200
    BOTTOM_TEXT_PAD_FROM_BOTTOM = 10

    # Placement
    BIG_TITLE_Y = 50
    GRAPH_Y = 600
    SMALL_TITLES_Y = 1400

    # - - - G R A P H - - - #

    TICKS_ON_GRAPH = 4
    TODAY_TICK_LABEL = "םויה"
    X_DAYS_AGO_LABEL = "םימי %s ינפל"

    FIG_SIZE = (6, 3)

    # - - -  F O N T S  - - - #

    FONTS_FOLDER = os.path.join(ASSETS_FOLDER, "fonts")
    TITLE_FONT_PATH = os.path.join(FONTS_FOLDER, "Heebo-Medium.ttf")
    VALUE_FONT_PATH = os.path.join(FONTS_FOLDER, "Heebo-Black.ttf")
    SUBTITLE_FONT_PATH = os.path.join(FONTS_FOLDER, "Heebo-Medium.ttf")
    BOTTOM_TEXT_FONT_PATH = os.path.join(FONTS_FOLDER, "Heebo-Medium.ttf")
    GRAPH_FONT_NAME = "Heebo"
    GRAPH_TITLE_WEIGHT = 800
    GRAPH_TICKS_WEIGHT = 500

    # Load fonts
    BIG_TITLE_FONT = ImageFont.truetype(
        TITLE_FONT_PATH, size=BIG_TITLE_SIZE)
    BIG_VALUE_FONT = ImageFont.truetype(
        VALUE_FONT_PATH, size=BIG_VALUE_SIZE)
    SMALL_TITLE_FONT = ImageFont.truetype(
        TITLE_FONT_PATH, size=SMALL_TITLE_SIZE)
    SMALL_VALUE_FONT = ImageFont.truetype(
        VALUE_FONT_PATH, size=SMALL_VALUE_SIZE)
    SMALL_SUBTITLE_FONT = ImageFont.truetype(
        SUBTITLE_FONT_PATH, size=SMALL_SUBTITLE_SIZE)
    BOTTOM_TEXT_FONT = ImageFont.truetype(
        BOTTOM_TEXT_FONT_PATH, size=BOTTOM_TEXT_SIZE)

    @classmethod
    def generate_tick_labels(cls, num_of_days):

        ticks = list()
        labels = list()

        if cls.TICKS_ON_GRAPH >= 1:
            ticks.append(num_of_days)
            labels.append(cls.TODAY_TICK_LABEL)

            if cls.TICKS_ON_GRAPH != 1:
                cur_tick = 0
                tick_jumps = int(num_of_days / (cls.TICKS_ON_GRAPH - 1))

                while (cur_tick + tick_jumps <= num_of_days):
                    cur_tick_days_ago = str(num_of_days-cur_tick)
                    labels.append(cls.X_DAYS_AGO_LABEL.replace(
                        '%s', cur_tick_days_ago))
                    ticks.append(cur_tick)
                    cur_tick += tick_jumps

        return [ticks, labels]

    @classmethod
    def save_plot_daydata(cls, data: List, path, dpi=None, title: str = None):

        # Load custom fonts
        fonts = font_manager.findSystemFonts(fontpaths=cls.FONTS_FOLDER)
        for font in fonts:
            font_manager.fontManager.addfont(font)

        _, ax = plt.subplots()

        if title:
            ax.set_title(title, fontname=cls.GRAPH_FONT_NAME,
                         fontweight=cls.GRAPH_TITLE_WEIGHT)

        # Set axes width
        mpl.rcParams['axes.linewidth'] = 2

        # Plot given data
        plt.plot(data, c="k", linewidth=3,
                 solid_capstyle="round", solid_joinstyle="round")

        # Add arrows to axes
        ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
        ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

        # Hide top and right axes
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        # Set (0,0) point to be the left bottom point in the graph
        pylab.xlim(xmin=0)
        pylab.ylim(ymin=0)

        # Add custom ticks
        [ticks, labels] = cls.generate_tick_labels(len(data))
        plt.xticks(ticks=ticks, labels=labels,
                   fontname=cls.GRAPH_FONT_NAME, fontweight=cls.GRAPH_TICKS_WEIGHT)
        plt.yticks(fontname=cls.GRAPH_FONT_NAME,
                   fontweight=cls.GRAPH_TICKS_WEIGHT)

        # Set figure size
        fig = plt.gcf()
        fig.set_size_inches(cls.FIG_SIZE[0], cls.FIG_SIZE[1])

        # Save the figure
        plt.savefig(path, dpi=dpi)

    @classmethod
    def add_graph(cls, data: List, base_img: Image.Image, title=None):

        TEMP_FILE_PATH = "TEMPFIG.png"

        # Generate the figure, and load it to PIL.
        cls.save_plot_daydata(data, TEMP_FILE_PATH, title=title, dpi=250)
        graph = Image.open(TEMP_FILE_PATH).convert("L")
        os.remove(TEMP_FILE_PATH)

        # Create the mask layer
        graph_mask = Image.new("L", size=base_img.size, color="white")

        # Paste the graph onto the graph mask, in the desired location.
        paste_x = int((graph_mask.width - graph.width) / 2)
        paste_y = cls.GRAPH_Y
        graph_mask.paste(graph, box=(paste_x, paste_y))

        # Now, `graph_mask` represents the true black and white mask.
        # It's time to composite it with the base image!

        # Create a solid with the desired figure color
        solid_graph = Image.new(
            "RGBA", size=base_img.size, color=cls.FIG_COLOR)

        return Image.composite(base_img, solid_graph, graph_mask)

    @classmethod
    def add_big_title(cls, base_img: Image.Image, title: str, value: str):

        draw = ImageDraw.Draw(base_img)
        x = base_img.width / 2
        y = cls.BIG_TITLE_Y

        draw.text((x, y), text=title, fill=cls.TITLE_COLOR,
                  font=cls.BIG_TITLE_FONT, anchor="ma")

        y += cls.PADDING_BETWEEN_BIG_TITLE_AND_VALUE

        draw.text((x, y), text=value, fill=cls.VALUE_COLOR,
                  font=cls.BIG_VALUE_FONT, anchor="ma")

    @classmethod
    def __add_small_title(cls, img: Image.Image, xy: Tuple[int, int], title: str, value: str, subtitle: str):

        draw = ImageDraw.Draw(img)
        x, y = xy

        draw.text((x, y), text=title, fill=cls.TITLE_COLOR,
                  font=cls.SMALL_TITLE_FONT, anchor="ma")

        y += cls.PADDING_BETWEEN_SMALL_TITLE_AND_VALUE

        draw.text((x, y), text=value, fill=cls.VALUE_COLOR,
                  font=cls.SMALL_VALUE_FONT, anchor="ma")

        y += cls.PADDING_BETWEEN_SMALL_VALUE_AND_SUBTITLE

        draw.text((x, y), text=subtitle, fill=cls.SUBTITLE_COLOR,
                  font=cls.SMALL_SUBTITLE_FONT, anchor="ma")

    @classmethod
    def add_small_titles_row(cls,
                             img: Image.Image,
                             titles_list: List[int],
                             values_list: List[int],
                             subtitles_list: List[int],
                             ):
        padding = cls.SMALL_TITLES_SIDE_PADDING
        x_jumps = (img.width - padding) / len(titles_list)
        x = (x_jumps + padding) / 2
        y = cls.SMALL_TITLES_Y

        for title, value, subtitle in zip(titles_list, values_list, subtitles_list):
            cls.__add_small_title(img, (x, y), title, value, subtitle)
            x += x_jumps

    @classmethod
    def generate_base_img(cls, new_cases: int):
        """ Returns an `Image` object that represents the background of the image. """

        # Choose random background
        files = os.listdir(cls.RANDOM_BACKGROUND_IMAGES_FOLDER)
        random_file = random.choice(files)

        # Load random background
        random_img = Image.open(
            os.path.join(cls.RANDOM_BACKGROUND_IMAGES_FOLDER, random_file))

        # Load background color image
        bg_color = cls.get_background_color(new_cases)
        background_img = Image.new("RGBA", random_img.size, color=bg_color)

        # Join two images
        return Image.alpha_composite(background_img, random_img)

    @classmethod
    def get_background_color(cls, new_cases: int):
        """ Returns a color that represents the number of new cases.
        If the number is high, the color will red, and if its low, it will slowly
        transform into orange -> yellow -> green -> blue.
        Uses the `cls.BACKGROUND_COLORS` dict
        """

        low_neighbor = None
        high_neighbor = None

        color_numbers = list(cls.BACKGROUND_COLORS.keys())
        color_numbers.sort()

        for cur_color_i, cur_color_num in enumerate(color_numbers):
            if new_cases <= cur_color_num:
                low_neighbor = cur_color_i - 1
                break

        # If the given num is lower then the minimum color num
        if cur_color_i == -1:
            return color_numbers[0]

        # If the given num is higher then the maximum color num
        if low_neighbor == None:
            return color_numbers[-1]

        # - - - - - - - - - - - - - - - - - - - #
        # If the given num is somewhere between #

        high_neighbor = color_numbers[low_neighbor + 1]
        low_neighbor = color_numbers[low_neighbor]

        high_neighbor_color = cls.BACKGROUND_COLORS[high_neighbor]
        low_neighbor_color = cls.BACKGROUND_COLORS[low_neighbor]

        new_cases_fixed = new_cases - low_neighbor
        neighbors_delta = high_neighbor - low_neighbor

        high_neighbor_force = new_cases_fixed / neighbors_delta
        low_neighbor_force = 1 - high_neighbor_force

        new_color = [
            int(
                (low_color_elem * low_neighbor_force) +
                (high_color_elem * high_neighbor_force)
            )
            for low_color_elem, high_color_elem in zip(low_neighbor_color, high_neighbor_color)
        ]

        return tuple(new_color)

    @classmethod
    def test_background_gradint(cls, from_: int, to: int, jumps: int = 1):

        width = math.ceil((to - from_) / jumps)
        height = int(width / 5)

        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        for cur_index, cur_color_num in enumerate(range(from_, to, jumps)):

            color = cls.get_background_color(cur_color_num)

            p1 = (cur_index, 0)
            p2 = (cur_index, height)

            draw.line([p1, p2], fill=color, width=1)

        return img

    @classmethod
    def add_bottom_test(cls, img: Image.Image, text: str):

        draw = ImageDraw.Draw(img)

        x = img.width / 2
        y = img.height - cls.BOTTOM_TEXT_PAD_FROM_BOTTOM

        draw.text(xy=(x, y), text=text, font=cls.BOTTOM_TEXT_FONT,
                  color=cls.BOTTOM_TEXT_COLOR, anchor="mb")


class PosterText:
    """
    Represents a collection of words, sencenses, or lines. Has a method called
    `to_image` that generates a special image of the words, where each of the
    words has the same width.

    Has two main methods:
    ---------------------
    1.  `set_truetype_font()` - sets the font of the poster
    2.  `to_image()` - generates the poster image
    """

    def __init__(self, *arguments: List):
        self._lines = self.__arguments_to_lines(arguments)
        self._font_args = list()
        self._font_kwargs = list()

    def __arguments_to_lines(self, arguments: List):
        """ Recives a list of arguments.
        Saves the strings and the lists only! """

        lines = list()
        for argument in arguments:
            if isinstance(argument, str):
                lines.append(argument)
            elif isinstance(argument, list):
                lines += argument
            else:
                logger.warning(
                    f"{argument} is not a supported argument. Ignoring...")

        return lines

    def set_truetype_font(self, *args, **kwargs):
        """ Saves the argument and keyword arguments that are passed, and uses
        them when generating the font of the poster image. """

        if "size" in kwargs:
            logger.warning(
                "Setting a poster font should not receive a size. Ignoring...")
            del kwargs["size"]

        self._font_args = args
        self._font_kwargs = kwargs

    def __build_font(self, size: int):
        """ Returns a font object, with the given size. """

        return ImageFont.truetype(*self._font_args, **self._font_kwargs, size=size)

    def __check_font_size(self,
                          font: ImageFont.ImageFont,
                          text: str,
                          target_size: int,
                          match_area: float = 1,
                          ) -> int:
        """ Returns `-1`, `0` or `1` depending on the relation between the given
        `target_size` and the actual size of the given font.

        *  1  - if the font is LARGER then the target value
        *  0  - if the font size and the target value are the same
        * -1  - if the font is SMALLER then the target value
        """

        width = font.getsize(text)[0]
        if abs(target_size - width) <= match_area:
            return 0   # a match
        elif width > target_size:
            return 1   # font is LARGER then expected
        else:
            return -1  # font is SMALLER then expected

    def __get_font(self,
                   text: str,
                   target_size: int,
                   min_size: int = 1,
                   max_size: int = None,
                   ) -> ImageFont.ImageFont:
        """ Recives the text, and returns a font object that matches the given text,
        with the matching size. """

        if max_size is None:

            new_size = min_size * 2
            font = self.__build_font(new_size)
            if self.__check_font_size(font, text, target_size) == -1:
                # if the generated font is smaller then needed
                return self.__get_font(text, target_size, min_size=new_size)
            else:
                # if larger (or equal)
                return self.__get_font(text, target_size,
                                       min_size=min_size, max_size=new_size)

        else:
            # If both min and max values are given

            new_size = int(sum([max_size, min_size]) / 2)
            font = self.__build_font(new_size)

            if (self.__check_font_size(font, text, target_size) == 0
                    or abs(min_size-max_size) <= 1):
                # a match found! return the current font
                return font

            elif self.__check_font_size(font, text, target_size) == -1:
                # if the generated font is smaller then needed
                return self.__get_font(text, target_size,
                                       min_size=new_size, max_size=max_size)

            elif self.__check_font_size(font, text, target_size) == 1:
                # if the generated font is larger then needed
                return self.__get_font(text, target_size,
                                       min_size=min_size, max_size=new_size)

    def to_image(self, width: int, padding: int = 0, color="black",):
        """ Generates and returns a PIL image object, representing the poster text. """
        return self.__to_image(
            width=width,
            padding=padding,
            color=color,
            left_lines=self._lines,
            cur_height=0,
        )

    def __to_image(self,
                   width: int,
                   padding: int,
                   color,

                   # recursize arguments
                   left_lines: List[str],
                   cur_height: int,
                   ):

        if len(left_lines) == 0:
            # Generate the image - empty transparent
            return Image.new("RGBA", (width, cur_height), color=(255, 255, 255, 0))

        line = get_display(left_lines.pop(0))
        font = self.__get_font(text=line, target_size=width)

        height = font.getsize(line)[1]
        if left_lines:
            # If current line is not the last one
            height += padding

        image = self.__to_image(
            width=width,
            padding=padding,
            color=color,
            left_lines=left_lines,
            cur_height=cur_height + height,
        )
        draw = ImageDraw.Draw(image)
        draw.text((0, cur_height), line, fill=color, font=font)
        return image


class SingleDataPoster:

    ASSETS_PATH = os.path.join("assets", "fa-svgs")
    ARROW_UP_ICON = Image.open(os.path.join(
        ASSETS_PATH, "arrow-alt-circle-up-solid.png"))
    ARROW_DOWN_ICON = ImageOps.flip(ARROW_UP_ICON)
    NO_CHANGE_ICON = Image.open(os.path.join(
        ASSETS_PATH, "no-change-circle-solid.png"))

    def __init__(self,
                 title: str,
                 now: int,
                 prev: int,
                 string_manager: StringManager = StringManager(),
                 ):
        self.string_manager = string_manager

        self._title = self.string_manager.convert(title)
        self._now = now
        self._prev = prev

    @property
    def title(self,) -> str:
        return self._title

    @property
    def now(self,) -> int:
        return self._now

    @property
    def prev(self,) -> int:
        return self._prev

    @property
    def delta(self,) -> int:
        return self.now - self.prev

    @property
    def delta_str(self,) -> str:
        return self.string_manager.delta_str(self.delta)

    @property
    def delta_precentage(self,) -> float:
        if self.prev == 0:
            return None

        one_precentage = self.prev / 100
        return self.delta / one_precentage

    @property
    def delta_precentage_str(self,):
        if self.delta_precentage is None:
            return self.string_manager.unavailable
        return f"{abs(self.delta_precentage):.1f}%"

    def to_image(self,
                 data_font: ImageFont.ImageFont,
                 title_font: ImageFont.ImageFont = None,
                 alter_font: ImageFont.ImageFont = None,

                 width=None,  # None = calculate automatically
                 color="black",

                 pad_title: int = 0,
                 pad_data: int = 0,

                 draw_line: bool = True,
                 line_length: int = None,  # None = max width.
                 line_width: int = 1,

                 icon_size: int = None,  # None = do not resize
                 pad_icon: int = 0,  # padding between icon and alter text
                 ):

        if title_font is None:
            title_font = data_font
        if alter_font is None:
            alter_font = data_font

        if width is None:
            width = self.__calc_image_width(
                data_font=data_font,
                title_font=title_font,
                alter_font=alter_font,
                draw_line=draw_line,
                line_length=line_length,
                icon_size=icon_size,
                pad_icon=pad_icon,
            )

        height = self.__calc_image_height(
            data_font=data_font,
            title_font=title_font,
            alter_font=alter_font,
            pad_title=pad_title,
            pad_data=pad_data,
            icon_size=icon_size,
        )

        # Create the image
        image = Image.new("RGBA", size=(width, height),
                          color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        x = int(width/2)
        y = 0

        # Add title to image
        draw.text((x, y), self.title, font=title_font, fill=color, anchor="ma")
        y += title_font.getsize(self.title)[1]
        y += pad_title

        # Add data to image
        draw.text((x, y), str(self.now), font=data_font,
                  fill=color, anchor="ma")
        y += data_font.getsize(str(self.now))[1]
        y += int(pad_data / 2)

        # Add line to image, if needed
        if draw_line:
            if line_length is None:
                line_x_start = 0
                line_x_end = width
            else:
                line_x_start = int((width - line_length) / 2)
                line_x_end = line_x_start + line_length

            draw.line((line_x_start, y, line_x_end, y),
                      fill=color, width=line_width)
        y += int(pad_data / 2)

        # Add alter data to image
        alter_img = self.alter_image(
            font=alter_font, color=color, icon_size=icon_size, pad_icon=pad_icon)
        x = int((width - alter_img.width) / 2)
        image.paste(alter_img, box=(x, y))

        return image

    def __calc_image_height(self,
                            data_font: ImageFont.ImageFont,
                            title_font: ImageFont.ImageFont,
                            alter_font: ImageFont.ImageFont,
                            pad_title: int,
                            pad_data: int,
                            icon_size: Optional[int]):
        alter_height = self.__calc_alter_height(
            font=alter_font, icon_size=icon_size
        )

        data_height = data_font.getsize(str(self.now))[1]
        title_height = title_font.getsize(self.title)[1]

        return math.ceil(sum([
            alter_height,
            data_height,
            title_height,
            pad_title,
            pad_data,
        ]))

    def alter_image(self,
                    font: ImageFont.ImageFont,
                    color="black",
                    icon_size: int = None,  # None = do not resize
                    pad_icon: int = 0,  # padding between icon and alter text
                    ):

        size = (self.__calc_alter_width(font=font, icon_size=icon_size, pad_icon=pad_icon),
                self.__calc_alter_height(font=font, icon_size=icon_size))

        image = Image.new("RGBA", color=(255, 255, 255, 0), size=size)

        # Load the icon
        icon = self.__get_matching_icon(color=color)
        if icon_size is not None:
            # Resize if needed
            if isinstance(icon_size, int):
                icon_size = (icon_size, icon_size)
            icon = icon.resize(icon_size)

        # Paste icon in the middle
        x = int((image.width - icon.width) / 2)
        y = int((image.height - icon.height) / 2)
        image.paste(icon, box=(x, y))

        # Generate draw object
        draw = ImageDraw.Draw(image)

        # Paste left text
        x = int(((image.width - icon.width) / 2) - pad_icon)
        y = int(image.height / 2)
        draw.text((x, y), self.delta_str,
                  fill=color, font=font, anchor="rm")

        # Paste right text
        x = int(((image.width + icon.width) / 2) + pad_icon)
        draw.text((x, y), self.delta_precentage_str,
                  fill=color, font=font, anchor="lm")

        return image

    def __get_matching_icon(self, color=None,) -> Image.Image:
        if self.delta == 0:
            icon = self.NO_CHANGE_ICON.copy()
        elif self.delta > 0:
            icon = self.ARROW_UP_ICON.copy()
        else:
            icon = self.ARROW_DOWN_ICON.copy()

        # Add color to the icon
        if color is not None:
            color_img = Image.new("RGB", size=icon.size, color=color)
            color_img.putalpha(icon.getchannel('A'))
            icon = color_img

        return icon

    def __calc_alter_width(self,
                           font: ImageFont.ImageFont,
                           icon_size: int,  # None = do not resize
                           pad_icon: int,  # padding between icon and alter text
                           ) -> int:
        if icon_size is None:
            icon_size = self.ARROW_UP_ICON.width

        alter_width = icon_size
        alter_width += pad_icon * 2
        alter_width += max(
            font.getsize(self.delta_str)[0],
            font.getsize(self.delta_precentage_str)[0]
        ) * 2

        return math.ceil(alter_width)

    def __calc_alter_height(self, font: ImageFont.ImageFont, icon_size: int) -> int:
        if icon_size is None:
            icon_size = self.__get_matching_icon().height

        return math.ceil(max(
            icon_size,
            font.getsize(self.delta_str)[1],
            font.getsize(self.delta_precentage_str)[1],
        ))

    def __calc_image_width(self,
                           data_font: ImageFont.ImageFont,
                           title_font: ImageFont.ImageFont,
                           alter_font: ImageFont.ImageFont,
                           draw_line: bool,
                           line_length: Optional[int],
                           icon_size: Optional[int],
                           pad_icon: int,
                           ) -> int:

        data_width = data_font.getsize(str(self.now))[0]
        title_width = title_font.getsize(self.title)[0]
        alter_width = self.__calc_alter_width(
            font=alter_font, icon_size=icon_size, pad_icon=pad_icon)

        if line_length is None:
            line_length = 0

        return math.ceil(max([
            data_width,
            title_width,
            line_length,
            alter_width,
        ]))
