from components.muntin_label import MuntinLabel
from components.utils import scale_point
from enums.colors import Colors


class Muntin:

    def __init__(self, panel_object):
        self.panel_object = panel_object

    def validate_muntin_x(self, x):
        """
        Args: x - int - x co-ordinate of a point

        Function checks if the x falls in between minx and max x of dlo; if not clamp it to min or max
        """
        if x < self.dlo_min_x:
            x = self.dlo_min_x
        elif x > self.dlo_max_x:
            x = self.dlo_max_x

        return x

    def validate_muntin_y(self, y):
        """
        Args: y - int - y co-ordinate of a point

        Function checks if the y falls in between min_y and max_y of dlo; if not clamp it to min or max
        """
        if y < self.dlo_min_y:
            y = self.dlo_min_y
        elif y > self.dlo_max_y:
            y = self.dlo_max_y

        return y

    def validate_muntin_points(self, points):
        """
        Args: points - ((x,y),(x1,y1)) - tuple of points to draw line bw

        Function checks if the points falls in the dlo area (check for overflow)
        and returns the updated points
        """
        x1, y1 = points[0][0], points[0][1]
        x2, y2 = points[1][0], points[1][1]

        x1 = self.validate_muntin_x(x1)
        x2 = self.validate_muntin_x(x2)

        y1 = self.validate_muntin_y(y1)
        y2 = self.validate_muntin_y(y2)

        return (x1, y1), (x2, y2)

    def draw_line(self, points, thickness=None):
        """
        Args: points - ((x,y),(x1,y1)) - tuple of points to draw line bw

        """
        # checks and invalidates if there is any overflow wrt dlo area
        points = self.validate_muntin_points(points)

        if thickness:
            # draw as a rectangle
            x1, y1 = points[0][0], points[0][1]
            x2, y2 = points[1][0], points[1][1]

            width = thickness * self.panel_object.scale_factor
            height = abs(y2 - y1)

            x = min(x1, x2)
            y = min(y1, y2)

            if height == 0:
                # its a horizontal line
                height = width
                width = abs(x2 - x1)

            # modify width and height such that it won't overflow the dlo_area
            if x + width > self.dlo_max_x:
                width = self.dlo_max_x - x

            if y + height > self.dlo_max_y:
                height = self.dlo_max_y - y

            self.panel_object.context.rectangle(x, y, width, height)
            self.panel_object.context.fill()
        else:
            # draw normal line
            self.panel_object.context.move_to(points[0][0], points[0][1])
            self.panel_object.context.line_to(points[1][0], points[1][1])
            self.panel_object.context.stroke()

    def draw_muntin_part_from_placements(self, part_data, x, y):
        for position in part_data['placement_positions']:

            if isinstance(position, (float, int)):
                scaled_start = position * self.panel_object.scale_factor
                scaled_part_length = part_data['length'] * self.panel_object.scale_factor

                if part_data['orientation'] == 'vertical':
                    start_point = (x + scaled_start, y)
                    end_point = (x + scaled_start, y + scaled_part_length)
                else:
                    start_point = (x, y + scaled_start)
                    end_point = (x + scaled_part_length, y + scaled_start)
            else:
                scaled_start_axis_1 = position[0] * self.panel_object.scale_factor
                scaled_start_axis_2 = position[1] * self.panel_object.scale_factor

                scaled_part_length = part_data['length'] * self.panel_object.scale_factor

                if part_data['orientation'] == 'vertical':
                    start_point = (x + scaled_start_axis_1, y + scaled_start_axis_2)
                    end_point = (x + scaled_start_axis_1, y + scaled_start_axis_2 + scaled_part_length)
                else:
                    start_point = (x + scaled_start_axis_2, y + scaled_start_axis_1)
                    end_point = (x + scaled_start_axis_2 + scaled_part_length, y + scaled_start_axis_1)

            self.draw_line((start_point, end_point), thickness=part_data.get('thickness', None))

    def draw_muntin(self):
        muntin_parameters = self.panel_object.muntin_parameters
        context = self.panel_object.context
        context.save()

        muntin_shape = self.panel_object.muntin_shape

        # calculate start x and y
        dlo_x_offset = (self.panel_object.scaled_width - self.panel_object.scaled_dlo_width) / 2
        dlo_y_offset = (self.panel_object.scaled_height - self.panel_object.scaled_dlo_height) / 2

        dlo_width = self.panel_object.scaled_dlo_width
        dlo_height = self.panel_object.scaled_dlo_height

        x = self.panel_object.x + dlo_x_offset
        y = self.panel_object.y + dlo_y_offset

        self.dlo_min_x = x
        self.dlo_min_y = y
        self.dlo_max_x = x + dlo_width
        self.dlo_max_y = y + dlo_height

        b_offset = 0.10 * dlo_width

        # start draw
        if muntin_shape:
            context.set_source_rgba(*Colors.BLACK)
            context.set_line_width(0.5)

            # Iterate over the sides and draw each line
            for side in muntin_shape.get('sides', []):

                segment = side.get('segment', {})

                if not segment:
                    continue

                p1 = scale_point(segment['p1'], self.panel_object.scale_factor)
                p2 = scale_point(segment['p2'], self.panel_object.scale_factor)
                b1 = scale_point(segment['b1'], self.panel_object.scale_factor)
                b2 = scale_point(segment['b2'], self.panel_object.scale_factor)

                # Move to the start point
                context.move_to(x + p1[0], y + p1[1])

                # Draw the Bezier curve
                context.curve_to(x + b1[0], y + b1[1], x + b2[0], y + b2[1],
                                      x + p2[0], y + p2[1])
                context.stroke()

            return

        elif self.panel_object.muntin_parts:
            # muntins from parts placements
            context.set_source_rgba(*Colors.BLACK)
            context.set_line_width(0.5)

            for part in self.panel_object.muntin_parts:
                self.draw_muntin_part_from_placements(part, x, y)

            # DRAW MUNTIN LABELS
            if self.panel_object.draw_muntin_label:
                # draw labels for vertical parts
                vertical_parts = [part for part in self.panel_object.muntin_parts if part['orientation'] == 'vertical']

                # a part can be placed at multiple points, gather each placement and keep it in ascending order
                vertical_parts = self.__sort_muntin_parts(vertical_parts)
                vertical_parts = self.__unique_position_parts(vertical_parts)

                self.draw_muntin_labels(vertical_parts)

                # horizontal parts
                horizontal_parts = [part for part in self.panel_object.muntin_parts if
                                    part['orientation'] == 'horizontal']

                # a part can be placed at multiple points, gather each placement and keep it in ascending order
                horizontal_parts = self.__sort_muntin_parts(horizontal_parts)
                horizontal_parts = self.__unique_position_parts(horizontal_parts)

                self.draw_muntin_labels(horizontal_parts)

            context.restore()
            return

        pattern = muntin_parameters.get('pattern', '')

        if not pattern:
            return

        context.set_source_rgba(*Colors.BLACK)
        context.set_line_width(0.5)

        if pattern == 'grid':
            rows = muntin_parameters['rows']
            columns = muntin_parameters['columns']
            if rows < 1 or columns < 1:
                return

            # draw vertical lines
            # x co-ordinate for end of the dlo
            terminate_x = x + dlo_width

            while x < terminate_x:
                x = x + dlo_width / columns
                self.draw_line(((x, y), (x, y + dlo_height)))

            # draw horizontal lines
            # reset x to initial value
            x = self.panel_object.x + dlo_x_offset

            # y co-ordinate for end of the dlo
            terminate_y = y + dlo_height

            while y < terminate_y:
                y = y + dlo_height / rows
                self.draw_line(((x, y), (x + dlo_width, y)))

        elif pattern in ['brittany-6', 'brittany-9']:
            self.draw_line(((x + b_offset, y), (x + b_offset, y + dlo_height)))
            self.draw_line(((x + dlo_width - b_offset, y), (x + dlo_width - b_offset, y + dlo_height)))

            self.draw_line(((x, y + dlo_height - b_offset), (x + dlo_width, y + dlo_height - b_offset)))

        if pattern == 'brittany-9':
            self.draw_line(((x, y + b_offset), (x + dlo_width, y + b_offset)))

        context.restore()

    def draw_muntin_labels(self, parts):
        previous_label = None
        for index, part in enumerate(parts):
            # Make a copy of previous_label
            current_previous_label = previous_label
            muntin_label = MuntinLabel(index, part, self, current_previous_label)
            muntin_label.draw()

            previous_label = muntin_label

    @staticmethod
    def __sort_muntin_parts(parts):
        """
            Sorts muntin parts according to positions, ascending from min to max
        """
        sorted_parts = []
        for part in parts:
            for position in part['placement_positions']:
                new_item = part.copy()
                new_item['placement_position'] = position
                del new_item['placement_positions']
                sorted_parts.append(new_item)

        # Sort the new list based on the 'placement_position' key
        sorted_parts.sort(
            key=lambda x: x['placement_position'] if isinstance(x['placement_position'], (float, int)) else
            x['placement_position'][0])

        return sorted_parts

    @staticmethod
    def __unique_position_parts(parts):
        """
            Filters out parts which are serially places on a same x/y index

            args: parts - list of parts
        """
        unique_positions = set()
        unique_parts = []

        for item in parts:
            position = item['placement_position'] if isinstance(item['placement_position'], (float, int)) else \
                item['placement_position'][0]
            if position not in unique_positions:
                unique_positions.add(position)
                unique_parts.append(item)

        return unique_parts
