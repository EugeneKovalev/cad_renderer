import math

import cairo

from components.shapes.shape_label import ShapeLabel
from enums.colors import Colors


class Triangle:
    def __init__(self, x=0, y=0, raw_params=None, scale_factor=1, draw_label=True, direction="left"):
        self._context = None
        self.parent_panel = None
        self.draw_label = draw_label

        self.x = x
        self.y = y
        self.raw_params = raw_params

        self.panel_type = raw_params['panel_type']
        self.name = raw_params['name'] if raw_params['panel_type'] == 'panel' else 'frame'

        self.scale_factor = scale_factor
        self.direction = direction
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

    def draw_triangle(self, x, y, width, height, thickness=1):
        """
        Draws a triangle with the specified coordinates, width and height.

        Args:
            x (int): The x-coordinate of the bottom-left corner of the triangle.
            y (int): The y-coordinate of the bottom-left corner of the triangle.
            width (int): The width of the triangle.
            height (int): The height of the triangle.
            thickness (int, optional): The thickness of the lines. Defaults to 1.
        """

        self.context.new_sub_path()
        self.context.save()
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(thickness)

        # draw bottom line
        self.context.move_to(x, y)
        self.context.line_to(x + width, y)

        # move to top point
        if self.direction == "right":
            self.context.line_to(x, y + height)
        else:
            self.context.line_to(x + width, y + height)

        # line to start point
        self.context.line_to(x, y)

        self.context.stroke()
        self.context.restore()

    def draw_shape(self):
        #  find the base angles
        top_angle = math.atan(self.scaled_width / self.scaled_height)
        bottom_angle = math.atan(self.scaled_height / self.scaled_width)

        # draw frame    
        self.draw_triangle(x=self.x, y=self.y, width=self.scaled_width, height=self.scaled_height,
                           thickness=2)

        if self.draw_label:
            width_label_cords = {
                "x1": self.x,
                "y1": self.y + self.scaled_height,
                "x2": self.x,
                "y2": self.y + self.scaled_height + 3 * ShapeLabel.LABEL_SIDE_LENGTH,
                "x3": self.x + self.scaled_width,
                "y3": self.y + self.scaled_height + 3 * ShapeLabel.LABEL_SIDE_LENGTH,
                "x4": self.x + self.scaled_width,
                "y4": self.y + self.scaled_height
            }
            width_label = ShapeLabel(panel=self, label_type='width', coordinates=width_label_cords)

            height_label_cords = {
                "x1": self.x,
                "y1": self.y,
                "x2": self.x - 3 * ShapeLabel.LABEL_SIDE_LENGTH,
                "y2": self.y,
                "x3": self.x - 3 * ShapeLabel.LABEL_SIDE_LENGTH,
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

            if panel['width'] > panel['height']:
                panel['height'] = self.height * 0.9
                panel['width'] = math.tan(top_angle) * panel['height']
            else:
                panel['width'] = self.width * 0.9
                panel['height'] = math.tan(bottom_angle) * panel['width']

            x_offset = (self.scaled_width - panel['width'] * self.scale_factor) / 3
            y_offset = (self.scaled_height - panel['height'] * self.scale_factor) / 3

            offset = min(x_offset, y_offset)
            if self.direction == "left":
                x_offset = self.scaled_width - panel['width'] * self.scale_factor - offset
            else:
                x_offset = offset

            child_panel = Triangle(x=self.x + x_offset, y=self.y + y_offset,
                                   raw_params=panel, scale_factor=self.scale_factor,
                                   draw_label=self.draw_label)

            self.child_labels.append(child_panel)

            self.raw_params = panel

            self.panel_type = panel['panel_type']
            self.name = panel['name'] if panel['panel_type'] == 'panel' else 'frame'

            # draw panel
            self.draw_triangle(x=self.x + x_offset, y=self.y + offset, width=self.scaled_width,
                               height=self.scaled_height, thickness=1)

            self.x = self.x + x_offset
            self.y = self.y + offset

            if self.draw_label:
                x1 = self.x
                x3 = self.x + self.scaled_width if self.direction == "left" else self.x + self.scaled_width
                width_label_cords = {
                    "x1": x1,
                    "y1": self.y + self.scaled_height,
                    "x2": x1,
                    "y2": self.y + self.scaled_height + 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                    "x3": x3,
                    "y3": self.y + self.scaled_height + 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                    "x4": x3,
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
