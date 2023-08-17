import random
import string
from functools import cached_property
from typing import Dict

import cairo

from components.shapes.arch import Arch
from components.shapes.circle import Circle
from components.shapes.eyebrow import Eyebrow
from components.shapes.half_circle import HalfCircle
from components.shapes.octagon import Octagon
from components.shapes.quarter_circle import QuarterCircle
from components.shapes.shape_label import ShapeLabel
from components.shapes.tombstone import Tombstone
from components.shapes.trapezoid import Trapezoid
from components.shapes.triangle import Triangle
from enums.colors import Colors


class Canvas:
    BORDER_LEFT_OFFSET, BORDER_RIGHT_OFFSET, BORDER_TOP_OFFSET, BORDER_BOTTOM_OFFSET = 10, 10, 10, 10

    def __init__(self, raw_params: Dict):
        self.filename = f"/tmp/{''.join(random.choice(string.ascii_uppercase) for _ in range(20))}.svg"
        self.raw_params = raw_params
        self.scale_factor = self.calculate_scale_factor()

        self.context = None
        self.__surface = None

    def draw(self):
        # set font size for shape label as 15 if image format is png
        if self.image_format == 'png':
            ShapeLabel.TEXT_SIZE = 15

        self.context = self.__create_context()
        shape = self.raw_params.get('shape', None)
        if not shape:
            self.__draw_frame(self.context)
        elif shape == 'halfcircle':
            hc = HalfCircle(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                            raw_params=self.raw_params, scale_factor=self.scale_factor,
                            draw_label=self.draw_label)
            hc.set_context(self.context)
            hc.draw_shape()
        elif shape == 'circle':
            c = Circle(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                       raw_params=self.raw_params, scale_factor=self.scale_factor, draw_label=self.draw_label)
            c.set_context(self.context)
            c.draw_shape()
        elif shape == 'octagon':
            c = Octagon(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                        raw_params=self.raw_params, scale_factor=self.scale_factor,
                        draw_label=self.draw_label)
            c.set_context(self.context)
            c.draw_shape()
        elif shape == 'eyebrow':
            e = Eyebrow(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                        raw_params=self.raw_params, scale_factor=self.scale_factor,
                        draw_label=self.draw_label)
            e.set_context(self.context)
            e.draw_shape()
        elif shape == 'arc':
            a = Arch(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                     raw_params=self.raw_params, scale_factor=self.scale_factor,
                     draw_label=self.draw_label)
            a.set_context(self.context)
            a.draw_shape()
        elif shape == 'tombstone':
            t = Tombstone(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                          raw_params=self.raw_params, scale_factor=self.scale_factor,
                          draw_label=self.draw_label)
            t.set_context(self.context)
            t.draw_shape()
        elif shape == 'triangle':
            triangle = Triangle(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width,
                                y=self.BORDER_BOTTOM_OFFSET, raw_params=self.raw_params, scale_factor=self.scale_factor,
                                draw_label=self.draw_label, direction=self.direction)
            triangle.set_context(self.context)
            triangle.draw_shape()

        elif shape == 'trapezoid':
            trapezoid = Trapezoid(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width,
                                  y=self.BORDER_BOTTOM_OFFSET, raw_params=self.raw_params,
                                  scale_factor=self.scale_factor, draw_label=self.draw_label, direction=self.direction)
            trapezoid.set_context(self.context)
            trapezoid.draw_shape()

        elif shape == 'quartercircle':
            quarter_circle = QuarterCircle(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width,
                                           y=self.BORDER_BOTTOM_OFFSET, raw_params=self.raw_params,
                                           scale_factor=self.scale_factor, draw_label=self.draw_label,
                                           direction=self.direction)
            quarter_circle.set_context(self.context)
            quarter_circle.draw_shape()

        if self.image_format == 'png':
            self.filename = f"/tmp/{''.join(random.choice(string.ascii_uppercase) for _ in range(20))}.png"
            self.__surface.write_to_png(self.filename)

        self.__close()

    # calculate total width with no scale factor
    def calculate_total_width(self):
        frame_width_with_labels = self.frame_width + self.left_positioned_labels_width
        return frame_width_with_labels + self.BORDER_LEFT_OFFSET + self.BORDER_RIGHT_OFFSET

    def calculate_scale_factor(self):
        max_canvas_width = self.max_canvas_width
        if max_canvas_width:
            total_width = self.calculate_total_width()
            return max_canvas_width / total_width
        return self.raw_params.get('scale_factor', 5)

    @cached_property
    def max_canvas_width(self):
        return self.raw_params.get('max_canvas_width')

    @cached_property
    def draw_label(self):
        return self.raw_params.get('draw_label', True)

    @cached_property
    def is_transparent(self):
        return self.raw_params.get('is_transparent', False)

    @cached_property
    def direction(self):
        return self.raw_params.get('direction', "left")

    @cached_property
    def image_format(self):
        return self.raw_params.get('image_format', "svg")

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
    def frame_height_2(self):
        return self.raw_params.get('height_2', 0)

    @cached_property
    def left_positioned_labels_width(self):
        # return 0 if draw_label is false
        if not self.draw_label:
            return 0

        from components.size_label import SizeLabel
        from components.panel import Panel

        if self.child_frames:
            num_of_child_labels = max([_['coordinates']['x'] for _ in self.child_frames]) * Panel.LABELS_PER_FRAME
        elif self.child_panels:
            if self.orientation == 'horizontal':
                num_of_child_labels = len(self.child_panels) * Panel.LABELS_PER_PANEL
            else:
                num_of_child_labels = Panel.LABELS_PER_PANEL
        else:
            num_of_child_labels = Panel.LABELS_PER_PANEL

        total_number_of_labels = num_of_child_labels + Panel.LABELS_PER_FRAME

        total_length_of_labels = total_number_of_labels * SizeLabel.LABEL_SIDE_LENGTH
        length_of_first_text = SizeLabel.TEXT_SIZE

        return SizeLabel.LABEL_OFFSET + length_of_first_text + total_length_of_labels

    @cached_property
    def top_positioned_labels_height(self):
        # return 0 if draw_label is false
        if not self.draw_label:
            return 0
        from components.panel import Panel
        from components.size_label import SizeLabel

        if self.child_frames:
            num_of_child_labels = max([_['coordinates']['y'] for _ in self.child_frames]) * Panel.LABELS_PER_FRAME
        elif self.child_panels:
            if self.orientation == 'horizontal':
                num_of_child_labels = Panel.LABELS_PER_PANEL
            else:
                num_of_child_labels = len(self.child_panels) * Panel.LABELS_PER_PANEL
        else:
            num_of_child_labels = Panel.LABELS_PER_PANEL

        total_number_of_labels = num_of_child_labels + Panel.LABELS_PER_FRAME

        total_length_of_labels = total_number_of_labels * SizeLabel.LABEL_SIDE_LENGTH
        length_of_first_text = SizeLabel.TEXT_SIZE

        return SizeLabel.LABEL_OFFSET + length_of_first_text + total_length_of_labels

    @cached_property
    def scaled_frame_width(self):
        return self.frame_width * self.scale_factor

    @cached_property
    def scaled_frame_height(self):
        return max(self.frame_height, self.frame_height_2) * self.scale_factor

    @cached_property
    def scaled_framed_width_with_labels(self):
        return self.scaled_frame_width + self.left_positioned_labels_width

    @cached_property
    def scaled_framed_height_with_labels(self):
        return self.scaled_frame_height + self.top_positioned_labels_height

    @cached_property
    def canvas_width(self):
        return self.scaled_framed_width_with_labels + self.BORDER_LEFT_OFFSET + self.BORDER_RIGHT_OFFSET

    @cached_property
    def canvas_height(self):
        return self.scaled_framed_height_with_labels + self.BORDER_TOP_OFFSET + self.BORDER_BOTTOM_OFFSET

    @cached_property
    def orientation(self):
        from components.panel import Panel

        if self.child_panels:
            return Panel.guess_orientation(self.frame_width, self.frame_height, self.child_panels)
        else:
            return 'horizontal'

    def __create_context(self):
        """
        Creates a context to draw onto
        :return: context
        """
        self.__surface = cairo.SVGSurface(self.filename, self.canvas_width, self.canvas_height)

        context = cairo.Context(self.__surface)
        if self.is_transparent:
            context.set_source_rgba(0, 0, 0, 0)
        else:
            context.set_source_rgba(*Colors.WHITE)
        context.paint()

        matrix = cairo.Matrix(yy=-1, y0=self.canvas_height)
        context.transform(matrix)

        return context

    def __draw_frame(self, context):
        from components.panel import Panel

        initial_frame = Panel(
            x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width,
            y=self.BORDER_BOTTOM_OFFSET,
            parent_panel=None,
            raw_params=self.raw_params,
            scale_factor=self.raw_params.get('scale_factor') or 5
        ).set_context(context)

        initial_frame.draw()

    def __close(self):
        self.__surface.__exit__()
