from functools import cached_property

import cairo

from enums.colors import Colors


class MuntinLabel:
    LABEL_SIDE_LENGTH = 20
    LABEL_OFFSET = 0

    STROKE_WIDTH = 0.5
    STROKE_FORMAT = [3, 3]  # fill 3 pixels & skip 3 pixels

    TEXT_SIZE = 10
    TEXT_OFFSET = 4

    def __init__(self, index, part, muntin_object, previous_label):
        """
        :param part:
        :param index: the position of the part
        :param muntin_object: instance of parent object of class Muntin
        :param previous_label: instance of class MuntinLabel
        """
        self.part = part
        self.index = index
        self.muntin_object = muntin_object
        self.previous_label = previous_label
        self.panel = muntin_object.panel_object
        self.type = 'vertical' if part['orientation'] == 'vertical' else 'horizontal'

    def draw(self):
        self._draw_label()
        self._draw_text()

    def text(self):
        position = self.placement_position

        if self.previous_label:
            position = self.placement_position - self.previous_label.placement_position - \
                       self.previous_label.part.get('thickness', 0)

        text = f"{self.__convert_to_fraction(position)}'"

        return text

    @cached_property
    def placement_position(self):
        if isinstance(self.part['placement_position'], (float, int)):
            return self.part['placement_position']
        else:
            return self.part['placement_position'][0]

    def scaled_part_thickness(self):
        return self.part.get('thickness', 0) * self.panel.scale_factor

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

        # if self.type == 'horizontal':
        #     self.context.rotate(math.pi / 2)

        self.context.show_text(self.text())
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

        (X1/Y1)                (X4/Y4)
        |                           |
        |                           |
        (X2/Y2---------------  (X3/Y3)

        OR

        (X4/Y4)--------(X3/Y3)
                            |
                            |
                            |
                            |
                            |
        (X1/Y1)--------(X2/Y2)
        """
        if self.type == 'vertical':
            if self.previous_label:
                return self.previous_label.x3 + self.previous_label.scaled_part_thickness()
            return self.muntin_object.dlo_min_x
        elif self.type == 'horizontal':
            return self.root_frame.x + self.root_frame.scaled_width

    @cached_property
    def y1(self):
        """
        Example:

        (X1/Y1)                (X4/Y4)
        |                           |
        |                           |
        (X2/Y2---------------  (X3/Y3)

        OR

        (X4/Y4)--------(X3/Y3)
                            |
                            |
                            |
                            |
                            |
        (X1/Y1)--------(X2/Y2)
        """

        if self.type == 'vertical':
            return self.root_frame.y
        elif self.type == 'horizontal':
            if self.previous_label:
                return self.previous_label.y3 + self.previous_label.scaled_part_thickness()
            return self.muntin_object.dlo_min_y

    @cached_property
    def x2(self):
        """
        Example:

        (X1/Y1)                (X4/Y4)
        |                           |
        |                           |
        (X2/Y2---------------  (X3/Y3)

        OR

        (X4/Y4)--------(X3/Y3)
                            |
                            |
                            |
                            |
                            |
        (X1/Y1)--------(X2/Y2)
        """

        if self.type == 'vertical':
            return self.x1
        elif self.type == 'horizontal':
            return self.x1 + self.LABEL_SIDE_LENGTH

    @cached_property
    def y2(self):
        """
        Example:

        (X1/Y1)                (X4/Y4)
        |                           |
        |                           |
        (X2/Y2---------------  (X3/Y3)

        OR

        (X4/Y4)--------(X3/Y3)
                            |
                            |
                            |
                            |
                            |
        (X1/Y1)--------(X2/Y2)
        """

        if self.type == 'vertical':
            return self.y1 - self.LABEL_SIDE_LENGTH
        elif self.type == 'horizontal':
            return self.y1

    @cached_property
    def x3(self):
        """
        Example:

        (X1/Y1)                (X4/Y4)
        |                           |
        |                           |
        (X2/Y2---------------  (X3/Y3)

        OR

        (X4/Y4)--------(X3/Y3)
                            |
                            |
                            |
                            |
                            |
        (X1/Y1)--------(X2/Y2)
        """
        if self.type == 'vertical':
            if self.previous_label:
                return self.previous_label.x3 + (
                        self.placement_position - self.previous_label.placement_position) * self.panel.scale_factor
            return self.x2 + self.placement_position * self.panel.scale_factor
        elif self.type == 'horizontal':
            return self.x2

    @cached_property
    def y3(self):
        """
        Example:

        (X1/Y1)                (X4/Y4)
        |                           |
        |                           |
        (X2/Y2---------------  (X3/Y3)

        OR

        (X4/Y4)--------(X3/Y3)
                            |
                            |
                            |
                            |
                            |
        (X1/Y1)--------(X2/Y2)
        """
        if self.type == 'vertical':
            return self.y2
        elif self.type == 'horizontal':
            if self.previous_label:
                return self.previous_label.y3 + (
                        self.placement_position - self.previous_label.placement_position) * self.panel.scale_factor
            return self.y2 + self.placement_position * self.panel.scale_factor

    @cached_property
    def x4(self):
        """
        Example:

        (X1/Y1)                (X4/Y4)
        |                           |
        |                           |
        (X2/Y2---------------  (X3/Y3)

        OR

        (X4/Y4)--------(X3/Y3)
                            |
                            |
                            |
                            |
                            |
        (X1/Y1)--------(X2/Y2)
        """
        if self.type == 'vertical':
            return self.x3
        elif self.type == 'horizontal':
            return self.x1

    @cached_property
    def y4(self):
        """
        Example:

        (X1/Y1)                (X4/Y4)
        |                           |
        |                           |
        (X2/Y2---------------  (X3/Y3)

        OR

        (X4/Y4)--------(X3/Y3)
                            |
                            |
                            |
                            |
                            |
        (X1/Y1)--------(X2/Y2)
        """
        if self.type == 'vertical':
            return self.y1
        elif self.type == 'horizontal':
            return self.y3

    @cached_property
    def text_x1(self):
        """
        Example:
        |                          |
        ----------------------------
        (X1/Y1)PANEL A: 300 1/2'(X2/Y2)

        """
        if self.type == 'vertical':
            if self.previous_label:
                return self.x2 + abs(len(self.text()) * (self.TEXT_SIZE / 2) - self.scaled_gap_bw_prev_part()) / 2
            return self.x2 + abs(
                len(self.text()) * (self.TEXT_SIZE / 2) - self.placement_position * self.panel.scale_factor) / 2
        elif self.type == 'horizontal':
            return self.x2 + self.TEXT_OFFSET

    @cached_property
    def text_y1(self):
        """
        Example:
            ------
                   |(X2/Y2)
                   |      0
                   |      1
                   |      :
                   |      L
                   |      E
                   |      N
                   |      A
                   |      P
                   |(X1/Y1)
            ------
        """
        if self.type == 'vertical':
            return self.y2 - self.TEXT_OFFSET - self.TEXT_SIZE
        elif self.type == 'horizontal':
            if self.previous_label:
                return self.y2 + abs(self.scaled_gap_bw_prev_part()) / 2 - self.TEXT_SIZE / 3
            return self.y2 + abs(self.placement_position * self.panel.scale_factor) / 2 - self.TEXT_SIZE / 3

    @cached_property
    def text_x2(self):
        """
        Example:
        |                          |
        ----------------------------
        (X1/Y1)PANEL A: 300 1/2'(X2/Y2)
        """
        if self.type == 'vertical':
            return self.text_x1 + len(self.text()) * (self.TEXT_SIZE / 2)
        elif self.type == 'horizontal':
            return self.text_x1

    def scaled_gap_bw_prev_part(self):
        return (self.placement_position - self.previous_label.placement_position) * self.panel.scale_factor - \
               self.previous_label.scaled_part_thickness()

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

            # in some cases, fraction is 1 / 1
            if fraction[1] == 1:
                return f"{natural_number + fraction[0]}"
            else:
                return f"{natural_number} {fraction[0]}/{fraction[1]}"
