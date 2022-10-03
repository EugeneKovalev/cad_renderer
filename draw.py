import itertools
import math
import random
import string
from functools import cached_property
from typing import Dict

import cairo

from colors import Colors

class SizeLabel:
    LABEL_SIDE_LENGTH = 20
    LABEL_OFFSET = 0

    STROKE_WIDTH = 0.5
    STROKE_FORMAT = [3, 3]  # fill 3 pixels & skip 3 pixels

    TEXT_SIZE = 10
    TEXT_OFFSET = 2

    def __init__(self, panel, label_type: str):
        """
        :param panel:
        :param label_type: width/height/dlo_width/dlo_height
        """
        self.panel = panel
        self.type = label_type

    def draw(self):
        self._draw_label()
        self._draw_text()

    @cached_property
    def text(self):
        text = f"{self.panel.name.upper()}"

        if self.panel.panel_type == 'frame' and self.panel.parent_panel:
            x_position = int(self.panel.raw_params['coordinates']['x'])
            y_position = int(self.panel.raw_params['coordinates']['y'])
            text = f"{text} <{x_position}, {y_position}>"

        if self.type == 'width':
            text = f"{text}: {self.__convert_to_fraction(self.panel.width)}'"
        elif self.type == 'dlo_width':
            text = f"{text} DLO: {self.__convert_to_fraction(self.panel.dlo_width)}'"
        elif self.type == 'height':
            text = f"{text}: {self.__convert_to_fraction(self.panel.height)}'"
        elif self.type == 'dlo_height':
            text = f"{text} DLO: {self.__convert_to_fraction(self.panel.dlo_height)}'"

        return text

    def _draw_label(self):
        self.context.save()
        self.context.set_source_rgba(*Colors.LIGHT_GREY)
        self.context.set_line_width(self.STROKE_WIDTH)
        self.context.set_dash(self.STROKE_FORMAT)

        self.context.move_to(self.x1, self.y1)
        self.context.line_to(self.x2, self.y2)
        self.context.line_to(self.x3, self.y3)
        self.context.line_to(self.x4, self.y4)
        self.context.stroke()
        self.context.restore()

    def _draw_text(self):
        self.context.save()
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_font_matrix(cairo.Matrix(xx=self.TEXT_SIZE, yy=-self.TEXT_SIZE))

        self.context.move_to(self.text_x1, self.text_y1)

        if self.type in ['height', 'dlo_height']:
            self.context.rotate(math.pi / 2)

        self.context.show_text(self.text)
        self.context.restore()

    @property
    def context(self) -> cairo.Context:
        return self.panel.context

    @property
    def root_frame(self):
        """Maximum level of the parental nesting for Size Labels is 2"""
        return self.panel.parent_panel or self.panel

    @cached_property
    def x1(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type == 'width':
            return self.panel.x
        elif self.type == 'dlo_width':
            offset = (self.panel.scaled_width - self.panel.scaled_dlo_width) / 2
            return self.panel.x + offset
        elif self.type in ['height', 'dlo_height']:
            return self.root_frame.x - self.LABEL_OFFSET

    @cached_property
    def y1(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """

        if self.type in ['width', 'dlo_width']:
            return self.root_frame.y + self.root_frame.scaled_height + self.LABEL_OFFSET
        elif self.type == 'height':
            return self.panel.y
        elif self.type == 'dlo_height':
            offset = (self.panel.scaled_height - self.panel.scaled_dlo_height) / 2
            return self.panel.y + offset

    @cached_property
    def x2(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            return self.x1
        elif self.type in ['height', 'dlo_height']:
            vertical_labels = [_ for _ in self.root_frame.size_labels if _.type in ['height', 'dlo_height']]
            intersected_labels = [_ for _ in vertical_labels if self.__has_overlap([self.y2, self.y3], [_.y2, max(_.y3, _.text_y2)])]

            if intersected_labels:
                min_x_point = min([min(_.x2, _.x3) for _ in intersected_labels])
            else:
                min_x_point = self.root_frame.x

            return min_x_point - self.LABEL_SIDE_LENGTH

    @cached_property
    def y2(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            horizontal_labels = [_ for _ in self.root_frame.size_labels if _.type in ['width', 'dlo_width']]

            intersected_labels = [_ for _ in horizontal_labels if self.__has_overlap([self.x2, self.x3], [_.x2, max(_.x3, _.text_x2)])]

            if intersected_labels:
                max_y_point = max([max(_.y2, _.y3) for _ in intersected_labels])
            else:
                max_y_point = self.root_frame.y + self.root_frame.scaled_height

            return max_y_point + self.LABEL_SIDE_LENGTH
        elif self.type in ['height', 'dlo_height']:
            return self.y1

    @cached_property
    def x3(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type == 'width':
            return self.x2 + self.panel.scaled_width
        elif self.type == 'dlo_width':
            return self.x2 + self.panel.scaled_dlo_width
        elif self.type in ['height', 'dlo_height']:
            return self.x2

    @cached_property
    def y3(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            return self.y2
        elif self.type == 'height':
            return self.y2 + self.panel.scaled_height
        elif self.type == 'dlo_height':
            return self.y2 + self.panel.scaled_dlo_height

    @cached_property
    def x4(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            return self.x3
        elif self.type in ['height', 'dlo_height']:
            return self.x1

    @cached_property
    def y4(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            return self.y1
        elif self.type in ['height', 'dlo_height']:
            return self.y3

    @cached_property
    def text_x1(self):
        """
        Example:
          (X1/Y1)PANEL A: 300 1/2'(X2/Y2)
        ----------------------------
        |                          |
        """
        if self.type in ['width', 'dlo_width']:
            return self.x2 + self.TEXT_OFFSET
        elif self.type in ['height', 'dlo_height']:
            return self.x2 - self.TEXT_OFFSET

    @cached_property
    def text_y1(self):
        """
        Example:
            ------
     (X2/Y2)|
           0|
           1|
           :|
           L|
           E|
           N|
           A|
           P|
     (X1/Y1)|
            ------
        """
        if self.type in ['width', 'dlo_width']:
            return self.y2 + self.TEXT_OFFSET
        elif self.type in ['height', 'dlo_height']:
            return self.y2 + self.TEXT_OFFSET

    @cached_property
    def text_x2(self):
        """
        Example:
          (X1/Y1)PANEL A: 300 1/2'(X2/Y2)
        ----------------------------
        |                          |
        """
        if self.type in ['width', 'dlo_width']:
            return self.text_x1 + len(self.text) * (self.TEXT_SIZE / 2)
        elif self.type in ['height', 'dlo_height']:
            return self.text_x1

    @cached_property
    def text_y2(self):
        """
        Example:
            ------
     (X2/Y2)|
           0|
           1|
           :|
           L|
           E|
           N|
           A|
           P|
     (X1/Y1)|
            ------
        """
        if self.type in ['width', 'dlo_width']:
            return self.text_y1
        elif self.type in ['height', 'dlo_height']:
            return self.text_y1 + len(self.text) * (self.TEXT_SIZE / 2)

    @staticmethod
    def __convert_to_fraction(original_number: float) -> str:
        """Converts 30.5 to 30 1/2 - this is a CAD convention in engineering"""
        rounded_number = round(original_number * 16) / 16
        natural_number = int(original_number)
        tail_number = rounded_number - natural_number

        if tail_number == 0:
            return str(natural_number)
        else:
            fraction = tail_number.as_integer_ratio()
            return f"{natural_number} {fraction[0]}/{fraction[1]}"

    @staticmethod
    def __has_overlap(interval1, interval2) -> bool:
        return bool(max(0, min(interval1[1], interval2[1]) - max(interval1[0], interval2[0])))


class Panel:
    SCALE_FACTOR = 5
    
    LABELS_PER_FRAME = 1
    LABELS_PER_PANEL = 2
    
    def __init__(self, x=0.0, y=0.0, parent_panel=None, raw_params=None):
        self._context = None

        self.x = x
        self.y = y
        self.parent_panel = parent_panel
        self.raw_params = raw_params

        self.panel_type = raw_params['panel_type']
        self.name = raw_params['name'] if raw_params['panel_type'] == 'panel' else 'frame'
        self.move_direction = raw_params.get('move_direction')

        self.child_panels = []
        self._size_labels = []

    @property
    def width(self):
        return self.raw_params['width']

    @property
    def height(self):
        return self.raw_params['height']

    @property
    def dlo_width(self):
        return self.raw_params['dlo_width']

    @property
    def dlo_height(self):
        return self.raw_params['dlo_height']

    @property
    def scaled_width(self):
        return self.width * self.SCALE_FACTOR

    @property
    def scaled_height(self):
        return self.height * self.SCALE_FACTOR

    @property
    def scaled_dlo_width(self):
        return self.dlo_width * self.SCALE_FACTOR

    @property
    def scaled_dlo_height(self):
        return self.dlo_height * self.SCALE_FACTOR

    def _draw_frame(self):
        self.context.save()

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(2)
        self.context.rectangle(self.x, self.y, self.scaled_width, self.scaled_height)
        self.context.stroke()

        self.context.restore()

    def _draw_panel(self):
        self.context.save()

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(1)

        self.context.rectangle(self.x, self.y, self.scaled_width, self.scaled_height)

        self.context.stroke()

        self.context.restore()

    def _draw_panel_dlo(self):
        self.context.save()

        dlo_x_offset = (self.scaled_width - self.scaled_dlo_width) / 2
        dlo_y_offset = (self.scaled_height - self.scaled_dlo_height) / 2

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(0.5)
        self.context.rectangle(self.x + dlo_x_offset, self.y + dlo_y_offset, self.scaled_dlo_width, self.scaled_dlo_height)
        self.context.stroke()

        self.context.restore()

    def _draw_child_frames(self):
        sort_by = lambda _: f"{_['coordinates']['y']}_{_['coordinates']['x']}"
        group_by = lambda _: _['coordinates']['y']

        raw_frames = sorted(self.raw_params.get('frames', []), key=sort_by)
        row__w__frames = {k: list(v) for k, v in itertools.groupby(raw_frames, key=group_by)}

        initial_x_offset = (self.scaled_width - self.scaled_dlo_width) / 2
        initial_y_offset = (self.scaled_height - self.scaled_dlo_height) / 2

        y1 = self.y + initial_y_offset
        for row, _frames in row__w__frames.items():
            x1 = self.x + initial_x_offset

            for raw_frame in _frames:
                frame = Panel(
                    x=x1,
                    y=y1,
                    parent_panel=self,
                    raw_params=raw_frame
                ).set_context(self.context).draw()
                self.child_panels.append(frame)

                x1 += frame.scaled_width

            y1 += max([_['height'] * self.SCALE_FACTOR for _ in _frames])

    def _draw_child_panels(self):
        total_child_width = sum([_['width'] for _ in self.raw_params.get('panels', [])]) * self.SCALE_FACTOR
        x_offset = (self.scaled_width - total_child_width) / 2

        previous_panel = None
        for child_panel in self.raw_params.get('panels', []):
            y_offset = (self.scaled_height - child_panel['height'] * self.SCALE_FACTOR) / 2

            if previous_panel:
                x_offset += previous_panel.scaled_width

            panel = Panel(
                x=self.x + x_offset,
                y=self.y + y_offset,
                parent_panel=self,
                raw_params=child_panel
            ).set_context(self.context).draw()

            self.child_panels.append(panel)

            previous_panel = panel

    def _draw_size_labels(self, _type='primary'):
        """
        :param _type: primary/dlo
        """
        if _type == 'primary':
            width_label = SizeLabel(panel=self, label_type='width')
            height_label = SizeLabel(panel=self, label_type='height')
            width_label.draw()
            height_label.draw()
            self._size_labels.append(width_label)
            self._size_labels.append(height_label)
        elif _type == 'dlo' and self.panel_type == 'panel':
            dlo_width_label = SizeLabel(panel=self, label_type='dlo_width')
            dlo_height_label = SizeLabel(panel=self, label_type='dlo_height')
            dlo_width_label.draw()
            dlo_height_label.draw()
            self._size_labels.append(dlo_width_label)
            self._size_labels.append(dlo_height_label)

    def _draw_move_direction(self):
        self.context.save()

        arrow_angle = math.pi
        arrow_length = 0
        arrow_x, arrow_y = 0, 0

        dlo_x_offset = (self.scaled_width - self.scaled_dlo_width) / 2
        dlo_y_offset = (self.scaled_height - self.scaled_dlo_height) / 2

        if self.move_direction == 'left':
            arrow_angle = math.pi

            arrow_x = self.x + dlo_x_offset + self.scaled_dlo_width
            arrow_y = self.y + dlo_y_offset + self.scaled_height / 2

        elif self.move_direction == 'up':
            arrow_angle = math.pi / 2

            arrow_x = self.x + dlo_x_offset + self.scaled_dlo_width / 2
            arrow_y = self.y + dlo_y_offset

        elif self.move_direction == 'down':
            arrow_angle = - math.pi / 2

            arrow_x = self.x + dlo_x_offset + self.scaled_dlo_width / 2
            arrow_y = self.y + dlo_y_offset + self.scaled_dlo_height

        elif self.move_direction == 'right':
            arrow_angle = 0

            arrow_x = self.x + dlo_x_offset
            arrow_y = self.y + dlo_y_offset + self.scaled_height / 2

        if self.move_direction in ['left', 'right']:
            arrow_length = self.scaled_dlo_width * 0.1
        elif self.move_direction in ['up', 'down']:
            arrow_length = self.scaled_dlo_height * 0.1

        arrowhead_angle = math.pi / 6
        arrowhead_length = arrow_length / 2.25

        self.context.set_source_rgba(0, 0, 0, 1)

        self.context.move_to(arrow_x, arrow_y)  # move to center of canvas

        self.context.rel_line_to(arrow_length * math.cos(arrow_angle), arrow_length * math.sin(arrow_angle))
        self.context.rel_move_to(-arrowhead_length * math.cos(arrow_angle - arrowhead_angle),
                                 -arrowhead_length * math.sin(arrow_angle - arrowhead_angle))
        self.context.rel_line_to(arrowhead_length * math.cos(arrow_angle - arrowhead_angle),
                                 arrowhead_length * math.sin(arrow_angle - arrowhead_angle))
        self.context.rel_line_to(-arrowhead_length * math.cos(arrow_angle + arrowhead_angle),
                                 -arrowhead_length * math.sin(arrow_angle + arrowhead_angle))

        self.context.set_line_width(1)
        self.context.stroke()

        self.context.restore()

    def draw(self):
        if self.raw_params.get('panels', []):
            self._draw_child_panels()
        elif self.raw_params.get('frames', []):
            self._draw_child_frames()

        if self.panel_type == 'frame':
            self._draw_frame()
        elif self.panel_type == 'panel':
            self._draw_panel()
            self._draw_panel_dlo()

        if not self.parent_panel:
            for child_panel in self.child_panels:
                child_panel._draw_size_labels(_type='dlo')

            for child_panel in self.child_panels:
                child_panel._draw_size_labels(_type='primary')

            self._draw_size_labels(_type='primary')

        if self.move_direction:
            self._draw_move_direction()

        return self

    @property
    def context(self) -> cairo.Context:
        if not self._context:
            raise NotImplementedError

        return self._context

    def set_context(self, context):
        """
        Sets a context to draw a panel onto
        """
        self._context = context

        return self

    @property
    def size_labels(self):
        child_panels_labels = list(itertools.chain(*[_._size_labels for _ in self.child_panels]))

        return self._size_labels + child_panels_labels


class Canvas:
    BORDER_OFFSET = 10

    def __init__(self, raw_params: Dict):
        self.filename = f"/tmp/{''.join(random.choice(string.ascii_uppercase) for _ in range(20))}.svg"
        self.raw_params = raw_params

        self.context = None
        self.__surface = None

    def draw(self):
        self.context = self.__create_context()

        self.__draw_frame(self.context)

        self.__close()

    @cached_property
    def panel_type(self):
        return self.raw_params['panel_type']

    @cached_property
    def child_frames(self):
        return self.raw_params.get('frames') or []

    @cached_property
    def child_panels(self):
        return self.raw_params.get('panels') or []

    @cached_property
    def frame_width(self):
        return self.raw_params['width']

    @cached_property
    def frame_height(self):
        return self.raw_params['height']
    
    @cached_property
    def left_positioned_labels_width(self):
        if self.child_frames:
            num_of_child_labels = max([_['coordinates']['x'] for _ in self.child_frames]) * Panel.LABELS_PER_FRAME
        elif self.child_panels:
            num_of_child_labels = len(self.child_panels) * Panel.LABELS_PER_PANEL
        else:
            num_of_child_labels = 0

        total_number_of_labels = num_of_child_labels + Panel.LABELS_PER_FRAME

        total_length_of_labels = total_number_of_labels * SizeLabel.LABEL_SIDE_LENGTH
        length_of_first_text = SizeLabel.TEXT_SIZE

        return SizeLabel.LABEL_OFFSET + length_of_first_text + total_length_of_labels

    @cached_property
    def top_positioned_labels_width(self):
        if self.child_frames:
            num_of_child_labels = max([_['coordinates']['y'] for _ in self.child_frames]) * Panel.LABELS_PER_FRAME
        elif self.child_panels:
            num_of_child_labels = Panel.LABELS_PER_PANEL
        else:
            num_of_child_labels = 0

        total_number_of_labels = num_of_child_labels + Panel.LABELS_PER_FRAME

        total_length_of_labels = total_number_of_labels * SizeLabel.LABEL_SIDE_LENGTH
        length_of_first_text = SizeLabel.TEXT_SIZE

        return SizeLabel.LABEL_OFFSET + length_of_first_text + total_length_of_labels
    
    @cached_property
    def scaled_frame_width(self):
        return self.frame_width * Panel.SCALE_FACTOR

    @cached_property
    def scaled_frame_height(self):
        return self.frame_height * Panel.SCALE_FACTOR

    @cached_property
    def scaled_framed_width_with_labels(self):
        return self.scaled_frame_width + self.left_positioned_labels_width
    
    @cached_property
    def scaled_framed_height_with_labels(self):
        return self.scaled_frame_height + self.top_positioned_labels_width

    @cached_property
    def canvas_width(self):
        return self.scaled_framed_width_with_labels + self.BORDER_OFFSET * 2

    @cached_property
    def canvas_height(self):
        return self.scaled_framed_height_with_labels + self.BORDER_OFFSET * 2

    def __create_context(self):
        """
        Creates a context to draw onto
        :return: context
        """
        self.__surface = cairo.SVGSurface(self.filename, self.canvas_width, self.canvas_height)

        context = cairo.Context(self.__surface)
        context.set_source_rgba(*Colors.WHITE)
        context.paint()

        matrix = cairo.Matrix(yy=-1, y0=self.canvas_height)
        context.transform(matrix)

        return context

    def __draw_frame(self, context):
        initial_frame = Panel(
            x=self.BORDER_OFFSET + self.left_positioned_labels_width,
            y=self.BORDER_OFFSET,
            parent_panel=None,
            raw_params=self.raw_params
        ).set_context(context)

        initial_frame.draw()

    def __close(self):
        self.__surface.__exit__()
