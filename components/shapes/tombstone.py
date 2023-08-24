import cairo
import math

from components.shapes.shape_label import ShapeLabel
from enums.colors import Colors


class Tombstone:
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
        return self.raw_params['height'] - self.width / 2

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

    def draw_arch(self, center_x, center_y, radius, thickness=1, start_angle=0.0):
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

    def draw_lines_center_touchpoints(self, center, touchpoints, center_y_offset=0):
        """draw multiple lines for muntin patterns: from center to multiple touchpoints on the curve"""
        center_x, center_y = center
        for touchpoint in touchpoints:
            x, y = touchpoint
            self.draw_line((center_x - x, center_y + y), (center_x, center_y + center_y_offset), 1)

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

    # draw vertical lines below the arc without including the starting and ending points
    def draw_vertical_lines(self, line_count):
        line_spacing = self.scaled_width / (line_count + 1)
        for i in range(line_count):
            x = line_spacing * (i + 1)
            self.draw_line((self.x + x, self.y), (self.x + x, self.y + self.scaled_height_2))

    # draw horizontal lines below the arc including the starting point
    def draw_horizontal_lines(self, line_count):
        line_spacing = self.scaled_height_2 / line_count
        for i in range(line_count):  # include starting point
            y = line_spacing * i
            self.draw_line((self.x, self.y + self.scaled_height_2 - y),
                           (self.x + self.scaled_width, self.y + self.scaled_height_2 - y))

    def draw_sun_rays(self, radius, sun_radius, sun_width, sun_height, center, rays_count, center_line_bigger=False):
        # find touch points to draw sun rays
        panel_touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, rays_count)
        sun_touch_points = self.find_arc_touch_points(sun_radius, sun_width, sun_height, rays_count)
        # draw sun ray lines
        center_x, center_y = center
        for i, (touchpoint_sun, touchpoint_panel) in enumerate(zip(sun_touch_points, panel_touch_points)):
            x1, y1 = touchpoint_panel
            x2, y2 = touchpoint_sun
            if i == len(sun_touch_points) // 2 and center_line_bigger:  # check if current iteration is at the center
                y2 -= sun_height
            self.draw_line((center_x - x1, center_y + y1),
                           (center_x - x2, center_y + y2 + self.scaled_height_2))

    def draw_sun(self, sun_height, sun_width):
        sun_radius = (sun_width ** 2 / (8 * sun_height)) + sun_height / 2
        sun_center_x = self.x + self.scaled_width / 2
        sun_center_y = self.y + self.scaled_height_2 - (sun_radius - sun_height)

        # Calculate the central angle of the chord
        central_angle = 2 * math.asin(sun_width / (2 * sun_radius))

        # Calculate the start angle by subtracting half of the central angle from pi/2 (90 degrees)
        start_angle = math.pi / 2 - (central_angle / 2)

        self.draw_arch(sun_center_x, sun_center_y, radius=sun_radius,
                       thickness=1, start_angle=start_angle)

    def find_arc_radius(self, arc_height, arc_width):
        return (arc_width ** 2 / (8 * arc_height)) + arc_height / 2

    def draw_muntin(self, pattern_name, radius, center):
        if pattern_name == '4 lite':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 3)
            self.draw_lines_center_touchpoints(center, touch_points)

        elif pattern_name == '3 lite':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 2)
            self.draw_lines_center_touchpoints(center, touch_points)

        elif pattern_name == '2x1 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 1)
            self.draw_lines_center_touchpoints(center, touch_points)

        elif pattern_name == '7 lite sunburst':
            # draw sun arch
            sun_height = self.scaled_width / 6
            sun_width = self.scaled_width / 3
            sun_radius = self.find_arc_radius(sun_height, sun_width)
            self.draw_sun(sun_height, sun_width)
            self.draw_sun_rays(radius, sun_radius, sun_width, sun_height, center, 3)

            # draw sun chord
            self.draw_line((self.x, self.y + self.scaled_height_2),
                           (self.x + self.scaled_width / 3, self.y + self.scaled_height_2))
            self.draw_line((self.x + self.scaled_width / 3 * 2, self.y + self.scaled_height_2),
                           (self.x + self.scaled_width, self.y + self.scaled_height_2))

            self.draw_vertical_lines(2)

        elif pattern_name == '6 lite sunburst through':
            # draw sun arch
            sun_height = self.scaled_width / 4
            sun_width = self.scaled_width / 2
            sun_radius = self.find_arc_radius(sun_height, sun_width)

            self.draw_sun(sun_height, sun_width)
            self.draw_sun_rays(radius, sun_radius, sun_width, sun_height, center, 3, center_line_bigger=True)
            self.draw_vertical_lines(3)

        elif pattern_name == '8 lite sunburst through':
            # draw sun arch
            sun_height = self.scaled_width / 4
            sun_width = self.scaled_width / 2
            self.draw_sun(sun_height, sun_width)

            self.draw_vertical_lines(3)

            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 3)
            self.draw_lines_center_touchpoints(center, touch_points)

        elif pattern_name == '5 lite sunburst with 3x1 colonial' or \
                pattern_name == 'arch 5 lite sunburst with 3x1 colonial':
            # draw sun arch
            sun_height = self.scaled_width / 6
            sun_width = self.scaled_width / 3
            sun_radius = self.find_arc_radius(sun_height, sun_width)
            self.draw_sun(sun_height, sun_width)
            self.draw_sun_rays(radius, sun_radius, sun_width, sun_height, center, 3)
            self.draw_vertical_lines(2)
            self.draw_horizontal_lines(1)

        elif pattern_name == 'arch 2 lite with 1x1 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 1)
            self.draw_lines_center_touchpoints(center, touch_points, center_y_offset=self.scaled_height_2)
            self.draw_horizontal_lines(1)

        elif pattern_name == 'arch 2 lite with 1x2 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 1)
            self.draw_lines_center_touchpoints(center, touch_points, center_y_offset=self.scaled_height_2)
            self.draw_horizontal_lines(2)

        elif pattern_name == 'arch 2 lite with 2x1 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 1)
            self.draw_lines_center_touchpoints(center, touch_points)
            self.draw_horizontal_lines(1)

        elif pattern_name == 'arch 2 lite with 2x2 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 1)
            self.draw_lines_center_touchpoints(center, touch_points)
            self.draw_horizontal_lines(2)

        elif pattern_name == 'arch 4 lite with 1x1 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 3)
            self.draw_lines_center_touchpoints(center, touch_points, center_y_offset=self.scaled_height_2)
            self.draw_horizontal_lines(1)

        elif pattern_name == 'arch 3 lite with 1x1 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 2)
            self.draw_lines_center_touchpoints(center, touch_points, center_y_offset=self.scaled_height_2)
            self.draw_horizontal_lines(1)

        elif pattern_name == 'arch 3 lite with 1x2 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 2)
            self.draw_lines_center_touchpoints(center, touch_points, center_y_offset=self.scaled_height_2)
            self.draw_horizontal_lines(2)

        elif pattern_name == 'arch 3 lite with 2x1 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 2)
            self.draw_lines_center_touchpoints(center, touch_points, center_y_offset=self.scaled_height_2)
            self.draw_vertical_lines(1)
            self.draw_horizontal_lines(1)

        elif pattern_name == 'arch 3 lite with 2x2 colonial':
            touch_points = self.find_arc_touch_points(radius, self.scaled_width, self.scaled_height, 2)
            self.draw_lines_center_touchpoints(center, touch_points, center_y_offset=self.scaled_height_2)
            self.draw_vertical_lines(1)
            self.draw_horizontal_lines(2)

        elif pattern_name == 'arch 3 lite sunburst with 3x2 colonial':
            sun_height = self.scaled_width / 6
            sun_width = self.scaled_width / 3
            sun_radius = self.find_arc_radius(sun_height, sun_width)
            self.draw_sun(sun_height, sun_width)
            self.draw_sun_rays(radius, sun_radius, sun_width, sun_height, center, 1)
            self.draw_vertical_lines(2)
            self.draw_horizontal_lines(2)

        elif pattern_name == 'arch 5 lite sunburst with 3x2 colonial':
            sun_height = self.scaled_width / 6
            sun_width = self.scaled_width / 3
            sun_radius = self.find_arc_radius(sun_height, sun_width)
            self.draw_sun(sun_height, sun_width)
            self.draw_sun_rays(radius, sun_radius, sun_width, sun_height, center, 3)
            self.draw_vertical_lines(2)
            self.draw_horizontal_lines(2)

        elif pattern_name == 'arch 5 lite sunburst with 1x1 colonial':
            sun_height = self.scaled_width / 6
            sun_width = self.scaled_width / 3
            sun_radius = self.find_arc_radius(sun_height, sun_width)
            self.draw_sun(sun_height, sun_width)
            self.draw_sun_rays(radius, sun_radius, sun_width, sun_height, center, 3)
            self.draw_horizontal_lines(1)

    def draw_shape(self):
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

            child_panel = Tombstone(x=self.x, y=self.y,
                                    raw_params=panel, scale_factor=self.scale_factor,
                                    draw_label=self.draw_label)

            self.child_labels.append(child_panel)

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
