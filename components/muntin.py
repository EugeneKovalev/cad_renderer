from enums.colors import Colors


class Muntin:

    def __init__(self, panel_object):
        self.panel_object = panel_object

    def draw_line(self, points, thickness=None):
        """
        Args: points - ((x,y),(x1,y1)) - tuple of points to draw line bw

        """

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

        # calculate start x and y
        dlo_x_offset = (self.panel_object.scaled_width - self.panel_object.scaled_dlo_width) / 2
        dlo_y_offset = (self.panel_object.scaled_height - self.panel_object.scaled_dlo_height) / 2

        dlo_width = self.panel_object.scaled_dlo_width
        dlo_height = self.panel_object.scaled_dlo_height

        x = self.panel_object.x + dlo_x_offset
        y = self.panel_object.y + dlo_y_offset

        self.dlo_min_x = x
        self.dlo_min_y = y

        b_offset = 0.10 * dlo_width

        # start draw
        if self.panel_object.muntin_parts:
            # muntins from parts placements
            context.set_source_rgba(*Colors.BLACK)
            context.set_line_width(0.5)

            for part in self.panel_object.muntin_parts:
                self.draw_muntin_part_from_placements(part, x, y)

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
