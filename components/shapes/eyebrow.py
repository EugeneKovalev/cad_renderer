import cairo
import math

from components.shapes.shape_label import ShapeLabel
from enums.colors import Colors


class Eyebrow:
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
    def height_2(self):
        return self.raw_params['height_2']

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
    def scaled_height_2(self):
        return self.height_2 * self.scale_factor

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

    def draw_arch(self, center_x, center_y, radius, thickness=1, start_angle=0.0, start_offset=0):
        self.context.new_sub_path()
        self.context.save()
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(thickness)

        self.context.arc(center_x, center_y, radius, start_angle, math.pi - start_angle)

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

    def draw_lines_center_touchpoints(self, center, touchpoints):
        """draw multiple lines for muntin patterns: from center to multiple touchpoints on the curve"""
        center_x, center_y = center
        for touchpoint in touchpoints:
            x, y = touchpoint
            self.draw_line((center_x - x, center_y + y), (center_x, center_y), 1)

    def draw_muntin(self, pattern_name, radius, center):
        if pattern_name == 'lite-4':
            touch_points = [(self.scaled_width / 2, self.scaled_height_2),
                            (0, self.scaled_height),
                            (-self.scaled_width / 2, self.scaled_height_2)]
            self.draw_lines_center_touchpoints(center, touch_points)

        elif pattern_name == 'alternative_design_sunburst':
            # draw sun
            self.draw_line((self.x + self.scaled_width / 3, self.y),
                           (self.x + self.scaled_width / 3, self.y + self.scaled_height_2 / 2))
            self.draw_line((self.x + self.scaled_width / 3 * 2, self.y),
                           (self.x + self.scaled_width / 3 * 2, self.y + self.scaled_height_2 / 2))
            # draw arc
            arc_height = self.scaled_height / 2 - self.scaled_height_2 / 2
            arc_width = self.scaled_width / 3
            radius = (arc_width ** 2 / (8 * arc_height)) + arc_height / 2
            center_x = self.x + self.scaled_width / 2
            center_y = self.y + self.scaled_height_2 / 2 - (radius - arc_height)

            # Calculate the central angle of the chord
            central_angle = 2 * math.asin(arc_width / (2 * radius))

            # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
            start_angle = math.pi / 2 - (central_angle / 2)
            self.draw_arch(center_x, center_y, radius=radius, thickness=1, start_angle=start_angle)

            # draw sun rays
            panel_touch_points = [(self.scaled_width / 2, self.scaled_height_2),
                                  (0, self.scaled_height),
                                  (-self.scaled_width / 2, self.scaled_height_2)]
            sun_touch_points = [(self.scaled_width / 6, self.scaled_height_2 / 2),
                                (0, self.scaled_height / 2),
                                (-self.scaled_width / 6, self.scaled_height_2 / 2)]
            center_x, center_y = center
            for touchpoint_sun, touchpoint_panel in zip(sun_touch_points, panel_touch_points):
                x1, y1 = touchpoint_panel
                x2, y2 = touchpoint_sun
                self.draw_line((center_x - x1, center_y + y1),
                               (center_x - x2, center_y + y2))
        elif pattern_name == 'colonial':
            # draw vertical lines
            vertical_muntin_spacing = self.scaled_width / 3
            half_chord_radius_diff = radius - self.scaled_width / 2
            side_arc_height = vertical_muntin_spacing + half_chord_radius_diff

            # calculate the chord length of side arc
            side_arc_chord = 2 * math.sqrt(radius ** 2 - (radius - side_arc_height) ** 2)
            mun_height = side_arc_chord / 2 - (radius - self.scaled_height)
            self.draw_line((self.x + self.scaled_width / 3, self.y),
                           (self.x + self.scaled_width / 3, self.y + mun_height))
            self.draw_line((self.x + self.scaled_width / 3 * 2, self.y),
                           (self.x + self.scaled_width / 3 * 2, self.y + mun_height))

            # draw horizontal lines
            self.draw_line((self.x, self.y + self.scaled_height_2),
                           (self.x + self.scaled_width, self.y + self.scaled_height_2))
            self.draw_line((self.x, self.y + self.scaled_height_2 / 2),
                           (self.x + self.scaled_width, self.y + self.scaled_height_2 / 2))

        elif 'brittany' in pattern_name:
            # set brittany offset as 4
            brittany_offset = 4 * self.scale_factor

            # draw arc
            arc_height = self.scaled_height - self.scaled_height_2
            radius = (self.scaled_width ** 2 / (8 * arc_height)) + arc_height / 2
            center_x = self.x + self.scaled_width / 2
            center_y = self.y + self.scaled_height_2 - (radius - arc_height) - brittany_offset
            # Calculate the central angle of the chord
            central_angle = 2 * math.asin(self.scaled_width / (2 * radius))
            # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
            start_angle = math.pi / 2 - (central_angle / 2)
            self.draw_arch(center_x=center_x, center_y=center_y, radius=radius, thickness=1, start_angle=start_angle)

            # draw vertical lines
            half_chord_radius_diff = radius - self.scaled_width / 2
            side_arc_height = brittany_offset + half_chord_radius_diff

            # calculate the chord length of side arc
            side_arc_chord = 2 * math.sqrt(radius ** 2 - (radius - side_arc_height) ** 2)
            mun_height = side_arc_chord / 2 - (radius - self.scaled_height)
            self.draw_line((self.x + brittany_offset, self.y),
                           (self.x + brittany_offset, self.y + mun_height))
            self.draw_line((self.x + self.scaled_width - brittany_offset, self.y),
                           (self.x + self.scaled_width - brittany_offset, self.y + mun_height))

            if pattern_name == 'lite_9_brittany':
                # draw horizontal line
                self.draw_line((self.x, self.y + brittany_offset),
                               (self.x + self.scaled_width, self.y + brittany_offset))

        elif pattern_name == 'sunburst':
            # draw sun
            radius = self.scaled_width / 4
            center_x = self.x + self.scaled_width / 2
            center_y = self.y
            self.draw_arch(center_x, center_y, radius=radius, thickness=1)

            # draw sun rays
            panel_touch_points = [(self.scaled_width / 2, self.scaled_height_2),
                                  (0, self.scaled_height),
                                  (-self.scaled_width / 2, self.scaled_height_2)]
            y_sun = math.sin(math.pi / 4) * radius
            sun_touch_points = [(y_sun, y_sun), (0, radius), (-y_sun, y_sun)]
            center_x, center_y = center
            for touchpoint_sun, touchpoint_panel in zip(sun_touch_points, panel_touch_points):
                x1, y1 = touchpoint_panel
                x2, y2 = touchpoint_sun
                self.draw_line((center_x - x1, center_y + y1),
                               (center_x - x2, center_y + y2))

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
        # difference between frame height 1 and height 2 should be equal to panel's
        height2_offset = self.height - self.height_2

        self.draw_line((self.x, self.y), (self.x + self.scaled_width, self.y), 2)
        self.draw_line((self.x, self.y), (self.x, self.y + self.scaled_height_2), 2)
        self.draw_line((self.x + self.scaled_width, self.y),
                       (self.x + self.scaled_width, self.y + self.scaled_height_2), 2)

        # draw arc
        arc_height = self.scaled_height - self.scaled_height_2
        radius = (self.scaled_width ** 2 / (8 * arc_height)) + arc_height / 2
        center_x = self.x + self.scaled_width / 2
        center_y = self.y + self.scaled_height_2 - (radius - arc_height)

        # Calculate the central angle of the chord
        central_angle = 2 * math.asin(self.scaled_width / (2 * radius))

        # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
        start_angle = math.pi / 2 - (central_angle / 2)
        self.draw_arch(center_x, center_y, radius=radius, thickness=2, start_angle=start_angle)

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
            x_offset = (self.scaled_width - panel['width'] * self.scale_factor) / 2
            y_offset = (self.scaled_height - panel['height'] * self.scale_factor) / 2

            self.x = self.x + x_offset
            self.y = self.y + y_offset

            child_panel = Eyebrow(x=self.x, y=self.y,
                                  raw_params=panel, scale_factor=self.scale_factor,
                                  draw_label=self.draw_label)

            self.child_labels.append(child_panel)

            # add height 2 in panel params
            if 'height_2' not in panel.keys():
                panel['height_2'] = panel['height'] - height2_offset + (self.height - panel['height']) / 2

            self.raw_params = panel

            self.panel_type = panel['panel_type']
            self.name = panel['name'] if panel['panel_type'] == 'panel' else 'frame'

            self.draw_line((self.x, self.y),
                           (self.x + self.scaled_width, self.y))
            self.draw_line((self.x, self.y),
                           (self.x, self.y + self.scaled_height_2))
            self.draw_line((self.x + self.scaled_width, self.y),
                           (self.x + self.scaled_width, self.y + self.scaled_height_2))

            # draw arc
            arc_height = self.scaled_height - self.scaled_height_2
            radius = (self.scaled_width ** 2 / (8 * arc_height)) + arc_height / 2
            center_x = self.x + self.scaled_width / 2
            center_y = self.y + self.scaled_height_2 - (radius - arc_height)

            # Calculate the central angle of the chord
            central_angle = 2 * math.asin(self.scaled_width / (2 * radius))

            # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
            start_angle = math.pi / 2 - (central_angle / 2)

            self.draw_arch(center_x=center_x,
                           center_y=center_y,
                           radius=radius,
                           thickness=1,
                           start_angle=start_angle)
            # draw muntins
            pattern_name = self.raw_params.get('muntin_pattern', None)
            if pattern_name:
                self.draw_muntin(pattern_name, radius, (center_x, self.y))

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
                    "y3": self.y + self.scaled_height,
                    "x4": self.x,
                    "y4": self.y + self.scaled_height
                }
                height_label = ShapeLabel(panel=self, label_type='height', coordinates=height_label_cords)
                width_label.draw()
                height_label.draw()
