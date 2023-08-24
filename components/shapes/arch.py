import math

import cairo

from components.shapes.shape_label import ShapeLabel
from enums.colors import Colors
import logging


class Arch:
    def __init__(self, x=0, y=0, raw_params=None, scale_factor=1, draw_label=True):
        self._context = None
        self.parent_panel = None
        self.draw_label = draw_label

        self.x = x
        self.y = y
        self.raw_params = raw_params

        self.panel_type = raw_params['panel_type']
        self.name = raw_params['name'] if raw_params['panel_type'] == 'panel' else 'frame'

        self.scale_factor = scale_factor
        self._size_labels = []
        self.child_labels = []

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
        return self.width * self.scale_factor

    @property
    def scaled_height(self):
        return self.height * self.scale_factor

    @property
    def scaled_dlo_width(self):
        return self.dlo_width * self.scale_factor

    @property
    def scaled_dlo_height(self):
        return self.dlo_height * self.scale_factor

    @property
    def size_labels(self):
        return self._size_labels

    @property
    def original_width(self):
        return self.original_width

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

    def draw_arch(self, center_x, center_y, radius, thickness=1, start_angle=0.0, start_offset=0):
        self.context.new_sub_path()
        self.context.save()
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(thickness)

        self.context.arc(center_x, center_y, radius, start_angle, math.pi - start_angle)

        y_change = radius - self.scaled_height
        x_change = self.scaled_width / 2

        self.draw_line((center_x - x_change, center_y + y_change), (center_x + x_change, center_y + y_change), thickness)

        self.context.stroke()
        self.context.restore()

    def draw_line(self, start, end, thickness=1):
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(thickness)
        self.context.set_line_join(cairo.LineJoin.ROUND)
        self.context.set_line_cap(cairo.LineCap.ROUND)
        start_x, start_y = start
        end_x, end_y = end

        self.context.save()
        self.context.move_to(start_x, start_y)
        self.context.line_to(end_x, end_y)
        self.context.stroke()

    def draw_lines_center_touchpoints(self, center, touchpoints, start_offset):
        """draw multiple lines for muntin patterns: from center to multiple touchpoints on the curve"""
        center_x, center_y = center
        for touchpoint in touchpoints:
            x, y = touchpoint
            self.draw_line((center_x - x, center_y + y + start_offset), (center_x, center_y + start_offset))

    def find_arc_touch_points(self, radius, arc_width, arc_height, touch_point_count):
        central_angle = 2 * math.asin(arc_width / (2 * radius))

        # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
        start_angle = math.pi / 2 - (central_angle / 2)
        angle_between_points = central_angle / (touch_point_count + 1)

        touch_points = []
        for i in range(touch_point_count):
            # Calculate the angle for each touch point
            touch_point_angle = start_angle + angle_between_points * (i + 1)

            # Calculate the coordinates of each touch point
            x = radius * math.cos(touch_point_angle)
            y = radius * math.sin(touch_point_angle) - (radius - arc_height)
            touch_points.append((x, y))

        return touch_points

    def draw_muntin(self, pattern_name, radius, center, y_offset, x_offset):
        center_x, center_y = center
        if pattern_name == 'lite-4':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 3)
            self.draw_lines_center_touchpoints(center, touch_points, y_offset)

        elif pattern_name == 'lite-3':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 2)
            self.draw_lines_center_touchpoints(center, touch_points, y_offset)

        elif pattern_name == 'colonial-2x1':
            touch_points = [(0, self.scaled_height)]
            self.draw_lines_center_touchpoints(center, touch_points, y_offset)

        elif pattern_name == 'sunburst_through':
            # draw sun arch
            sun_height = self.scaled_height / 2
            sun_width = self.scaled_width / 2

            sun_radius = (sun_width ** 2 / (8 * sun_height)) + sun_height / 2
            center_y = self.y - (sun_radius - sun_height)

            # Calculate the central angle of the chord
            central_angle = 2 * math.asin(sun_width / (2 * sun_radius))

            # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
            start_angle = math.pi / 2 - (central_angle / 2)
            self.draw_arch(center_x, center_y + y_offset, radius=sun_radius,
                           thickness=1, start_angle=start_angle)

            # draw inclined lines
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 3)
            self.draw_lines_center_touchpoints(center, touch_points, y_offset)

        elif pattern_name == 'sunburst':
            # draw sun arch
            sun_height = self.scaled_height / 2
            sun_width = self.scaled_width / 2
            sun_radius = (sun_width ** 2 / (8 * sun_height)) + sun_height / 2

            sun_center_y = self.y - (sun_radius - sun_height) + y_offset

            # Calculate the central angle of the chord
            central_angle = 2 * math.asin(sun_width / (2 * sun_radius))

            # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
            start_angle = math.pi / 2 - (central_angle / 2)
            self.draw_arch(center_x, sun_center_y, radius=sun_radius,
                           thickness=1, start_angle=start_angle)

            # draw lines
            panel_touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 3)
            sun_touch_points = self.find_arc_touch_points(sun_radius, sun_width, sun_height, 3)

            center_x, center_y = center
            for touchpoint_sun, touchpoint_panel in zip(sun_touch_points, panel_touch_points):
                x1, y1 = touchpoint_panel
                x2, y2 = touchpoint_sun
                self.draw_line((center_x - x1, center_y + y1 + y_offset),
                               (center_x - x2, center_y + y2 + y_offset))

        elif pattern_name == 'colonial-3x1':
            vertical_muntin_spacing = self.scaled_width / 3
            half_chord_radius_diff = radius - self.scaled_width / 2
            side_arc_height = vertical_muntin_spacing + half_chord_radius_diff

            # Calculate the chord length of side arc
            side_arc_chord = 2 * math.sqrt(radius**2 - (radius - side_arc_height)**2)
            mun_height = side_arc_chord / 2 - (radius - self.scaled_height)
            self.draw_line((center_x - vertical_muntin_spacing/2, center_y + mun_height + y_offset),
                           (center_x - vertical_muntin_spacing/2, center_y + y_offset))
            self.draw_line((center_x + vertical_muntin_spacing/2, center_y + mun_height + y_offset),
                           (center_x + vertical_muntin_spacing/2, center_y + y_offset))

        elif pattern_name == 'colonial-3x2':
            vertical_muntin_spacing = self.scaled_width / 3
            half_chord_radius_diff = radius - self.scaled_width / 2
            side_arc_height = vertical_muntin_spacing + half_chord_radius_diff

            # Calculate the chord length of side arc
            side_arc_chord = 2 * math.sqrt(radius**2 - (radius - side_arc_height)**2)
            mun_height = side_arc_chord / 2 - (radius - self.scaled_height)

            # draw vertical lines
            self.draw_line((center_x - vertical_muntin_spacing/2, center_y + mun_height + y_offset),
                           (center_x - vertical_muntin_spacing/2, center_y + y_offset))
            self.draw_line((center_x + vertical_muntin_spacing/2, center_y + mun_height + y_offset),
                           (center_x + vertical_muntin_spacing/2, center_y + y_offset))

            # draw horizontal line
            y = self.scaled_height/2
            mun_length = 2 * math.sqrt(radius ** 2 - (radius - y) ** 2)
            self.draw_line((center_x - mun_length/2, center_y + y + y_offset),
                           (center_x + mun_length/2, center_y + y + y_offset))

    def calculate_arc_parameters(self, height, width, total_width):
        radius = (width ** 2 / (8 * height)) + height / 2
        center_x = self.x + total_width / 2
        center_y = self.y - (radius - height)

        # Calculate the central angle of the chord
        central_angle = 2 * math.asin(width / (2 * radius))

        # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
        start_angle = math.pi / 2 - (central_angle / 2)

        return center_x, center_y, radius, start_angle

    def draw_shape(self):
        total_width = self.scaled_width
        center_x, center_y, radius, start_angle = self.calculate_arc_parameters(self.scaled_height,
                                                                                self.scaled_width,
                                                                                total_width)
        self.draw_arch(center_x, center_y, radius=radius,
                       thickness=2, start_angle=start_angle)

        if self.draw_label:
            width_label_cords = {
                "x1": self.x,
                "y1": self.y + self.scaled_height,
                "x2": self.x,
                "y2": self.y + self.scaled_height + 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                "x3": self.x + self.scaled_width,
                "y3": self.y + self.scaled_height + 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                "x4": self.x + self.scaled_width,
                "y4": self.y + self.scaled_height
            }
            width_label = ShapeLabel(panel=self, label_type='width', coordinates=width_label_cords)

            height_label_cords = {
                "x1": self.x,
                "y1": self.y,
                "x2": self.x - 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                "y2": self.y,
                "x3": self.x - 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                "y3": self.y + self.scaled_height,
                "x4": self.x,
                "y4": self.y + self.scaled_height
            }
            height_label = ShapeLabel(panel=self, label_type='height', coordinates=height_label_cords)
            width_label.draw()
            height_label.draw()
            self._size_labels.append(width_label)
            self._size_labels.append(height_label)

        for panel in self.raw_params['panels']:
            center_x = self.x + self.scaled_width / 2
            x_offset = (self.scaled_width - panel['width'] * self.scale_factor)
            y_offset = (self.scaled_height - panel['height'] * self.scale_factor) / 2

            ## to avoid the panel having insufficient width, adjust the panel width based on the panel height.
            # original_width is used for labeling panel width
            panel['original_width'] = panel['width']
            sagitta = self.scaled_height - y_offset
            offset_chord = 2 * math.sqrt((2 * radius * sagitta) - (sagitta ** 2))
            panel['width'] = (offset_chord - y_offset*2) / self.scale_factor

            child_panel = Arch(x=self.x + x_offset, y=self.y + y_offset,
                                     raw_params=panel, scale_factor=self.scale_factor,
                                     draw_label=self.draw_label)

            self.child_labels.append(child_panel)

            self.raw_params = panel

            self.panel_type = panel['panel_type']
            self.name = panel['name'] if panel['panel_type'] == 'panel' else 'frame'

            radius = self.scaled_width ** 2 / (8 * self.scaled_height) + self.scaled_height / 2
            center_y = self.y - (radius - self.scaled_height - y_offset)

            # Calculate the central angle of the chord
            central_angle = 2 * math.asin(self.scaled_width / (2 * radius))

            # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
            start_angle = math.pi / 2 - (central_angle / 2)

            self.draw_arch(center_x=center_x,
                           center_y=center_y,
                           radius=radius,
                           thickness=1,
                           start_angle=start_angle,
                           start_offset=x_offset)
            # draw muntins
            pattern_name = self.raw_params.get('muntin_pattern', None)
            if pattern_name:
                self.draw_muntin(pattern_name, radius, (center_x, self.y), y_offset, x_offset)

            self.x = self.x + y_offset
            self.y = self.y + y_offset

            if self.draw_label:
                width_label_cords = {
                    "x1": self.x,
                    "y1": self.y + self.scaled_height,
                    "x2": self.x,
                    "y2": self.y + self.scaled_height + ShapeLabel.LABEL_SIDE_LENGTH,
                    "x3": self.x + self.scaled_width,
                    "y3": self.y + self.scaled_height + ShapeLabel.LABEL_SIDE_LENGTH,
                    "x4": self.x + self.scaled_width,
                    "y4": self.y + self.scaled_height
                }
                width_label = ShapeLabel(panel=self, label_type='width', coordinates=width_label_cords)

                height_label_cords = {
                    "x1": self.x,
                    "y1": self.y,
                    "x2": self.x - ShapeLabel.LABEL_SIDE_LENGTH,
                    "y2": self.y,
                    "x3": self.x - ShapeLabel.LABEL_SIDE_LENGTH,
                    "y3": self.y + self.scaled_height - y_offset,
                    "x4": self.x,
                    "y4": self.y + self.scaled_height - y_offset
                }
                height_label = ShapeLabel(panel=self, label_type='height', coordinates=height_label_cords)
                width_label.draw()
                height_label.draw()
