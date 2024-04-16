import math

import cairo

from components.shapes.shape_label import ShapeLabel
from components.utils import find_asin
from enums.colors import Colors


class HalfCircle:
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
        if self.raw_params.get('height_width_2x', True):
            return self.height * 2
        else:
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
        if self.raw_params.get('height_width_2x', True):
            return self.scaled_height * 2
        else:
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

    def draw_half_circle(self, center_x, center_y, radius, thickness=1, start_angle=0.0, start_offset=0):
        self.context.new_sub_path()
        self.context.save()
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(thickness)

        self.context.arc(center_x, center_y, radius, start_angle, math.pi - start_angle)

        if start_angle:
            x_change = radius - math.sqrt(radius ** 2 - start_offset ** 2)
            y_change = start_offset
        else:
            x_change = 0
            y_change = 0

        # self.context.move_to(center_x - radius + x_change, center_y + y_change)
        # self.context.line_to(center_x + radius - x_change, center_y + y_change)

        self.draw_line((center_x - radius + x_change, center_y + y_change),
                       (center_x + radius - x_change, center_y + y_change))
        self.context.stroke()
        self.context.restore()

    def draw_line(self, start, end):

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(1)

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
            self.draw_line((center_x - x, center_y + y), (center_x, center_y + start_offset))

    def draw_muntin(self, pattern_name, radius, center, start_offset):
        center_x, center_y = center

        if pattern_name == 'lite-4':
            y = math.sin(math.pi / 4) * radius
            touchpoints = [(-y, y), (0, radius), (y, y)]
            self.draw_lines_center_touchpoints(center, touchpoints, start_offset)

        elif pattern_name == 'lite-3':
            y = math.sin(math.pi / 3) * radius
            x = math.cos(math.pi / 3) * radius
            touchpoints = [(-x, y), (x, y)]
            self.draw_lines_center_touchpoints(center, touchpoints, start_offset)

        elif pattern_name == 'colonial-2x1':
            touchpoints = [(0, radius)]
            self.draw_lines_center_touchpoints(center, touchpoints, start_offset)

        elif pattern_name == 'sunburst_through':
            # draw inclined lines
            y = math.sin(math.pi / 4) * radius
            touchpoints = [(-y, y), (0, radius), (y, y)]
            self.draw_lines_center_touchpoints(center, touchpoints, start_offset)

            # draw inner semi circle
            inner_radius = self.scaled_width / 4
            start_angle = find_asin(start_offset / inner_radius)

            self.draw_half_circle(center_x=self.x + self.scaled_width / 2 + start_offset,
                                  center_y=self.y,
                                  radius=inner_radius,
                                  thickness=1,
                                  start_angle=start_angle,
                                  start_offset=start_offset)

        elif pattern_name == 'sunburst':
            # outer touchpoints
            y_outer = math.sin(math.pi / 4) * radius
            outer_touchpoints = [(-y_outer, y_outer), (0, radius), (y_outer, y_outer)]

            # inner touchpoints
            y_inner = math.sin(math.pi / 4) * radius / 2
            inner_touchpoints = [(-y_inner, y_inner), (0, radius / 2), (y_inner, y_inner)]

            center_x, center_y = center
            for touchpoint_inner, touchpoint_outer in zip(inner_touchpoints, outer_touchpoints):
                x1, y1 = touchpoint_outer
                x2, y2 = touchpoint_inner
                self.draw_line((center_x - x1, center_y + y1), (center_x - x2, center_y + y2))

            # draw inner semi circle
            inner_radius = self.scaled_width / 4
            start_angle = find_asin(start_offset / inner_radius)
            self.draw_half_circle(center_x=self.x + self.scaled_width / 2 + start_offset, center_y=self.y,
                                  radius=inner_radius, thickness=1, start_angle=start_angle, start_offset=start_offset)

        elif pattern_name == 'alternative_design_sunburst':
            # outer touchpoints
            y_outer = math.sin(math.pi / 4) * radius
            outer_touchpoints = [(-y_outer, y_outer), (0, radius), (y_outer, y_outer)]

            # inner touchpoints
            y_inner = math.sin(math.pi / 4) * radius / 2
            inner_touchpoints = [(-y_inner, y_inner), (0, radius / 2), (y_inner, y_inner)]

            for touchpoint_inner, touchpoint_outer in zip(inner_touchpoints, outer_touchpoints):
                x1, y1 = touchpoint_outer
                x2, y2 = touchpoint_inner
                self.draw_line((center_x - x1, center_y + y1), (center_x - x2, center_y + y2))

            # draw vertical pillars
            self.draw_line((center_x - y_inner, center_y + y_inner), (center_x - y_inner, center_y + start_offset))
            self.draw_line((center_x + y_inner, center_y + y_inner), (center_x + y_inner, center_y + start_offset))

            # draw inner semi circle
            inner_radius = self.scaled_width / 4
            self.draw_half_circle(center_x=self.x + self.scaled_width / 2 + start_offset, center_y=self.y,
                                  radius=inner_radius, thickness=1, start_angle=math.pi / 4, start_offset=start_offset)

        elif pattern_name == 'colonial-3x1':
            y = math.sqrt(radius ** 2 - radius ** 2 / 9)
            x = radius / 3

            self.draw_line((center_x - x, center_y + y), (center_x - x, center_y + start_offset))
            self.draw_line((center_x + x, center_y + y), (center_x + x, center_y + start_offset))

        elif pattern_name == 'colonial-3x2':
            y = math.sqrt(radius ** 2 - radius ** 2 / 9)
            x = radius / 3

            self.draw_line((center_x - x, center_y + y), (center_x - x, center_y + start_offset))
            self.draw_line((center_x + x, center_y + y), (center_x + x, center_y + start_offset))

            # horizontal line
            x = math.sqrt(radius ** 2 - radius ** 2 / 4)
            y = radius / 2

            self.draw_line((center_x - x, center_y + y), (center_x + x, center_y + y))

    def draw_shape(self):
        # draw frame
        outer_radius = self.scaled_width / 2
        self.draw_half_circle(center_x=self.x + self.scaled_width / 2, center_y=self.y, radius=outer_radius,
                              thickness=2)

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
            x_offset = (self.scaled_height - panel['height'] * self.scale_factor)
            y_offset = (self.scaled_height - panel['height'] * self.scale_factor) / 2

            child_panel = HalfCircle(x=self.x + x_offset, y=self.y + x_offset,
                                     raw_params=panel, scale_factor=self.scale_factor,
                                     draw_label=self.draw_label)

            self.child_labels.append(child_panel)

            self.raw_params = panel

            self.panel_type = panel['panel_type']
            self.name = panel['name'] if panel['panel_type'] == 'panel' else 'frame'

            # in case of inner panels, half circle is cur at the base, find the start angle for that
            radius = self.scaled_height
            start_angle = find_asin(x_offset / radius)

            self.draw_half_circle(center_x=self.x + self.scaled_height + x_offset,
                                  center_y=self.y,
                                  radius=radius,
                                  thickness=1,
                                  start_angle=start_angle,
                                  start_offset=x_offset)
            # draw muntins
            pattern_name = self.raw_params.get('muntin_pattern', None)
            if pattern_name:
                self.draw_muntin(pattern_name, radius, (self.x + self.scaled_height + x_offset, self.y), x_offset)

            self.x = self.x + x_offset
            self.y = self.y + x_offset

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
                    "y3": self.y + self.scaled_height - x_offset,
                    "x4": self.x,
                    "y4": self.y + self.scaled_height - x_offset
                }
                height_label = ShapeLabel(panel=self, label_type='height', coordinates=height_label_cords)
                width_label.draw()
                height_label.draw()
