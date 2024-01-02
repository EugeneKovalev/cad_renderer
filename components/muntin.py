from enums.colors import Colors


class Muntin:

    def __init__(self):
        pass

    @staticmethod
    def draw_line(context, points):
        """
        Args: points - ((x,y),(x1,y1)) - tuple of points to draw line bw

        """
        context.move_to(points[0][0], points[0][1])
        context.line_to(points[1][0], points[1][1])
        context.stroke()

    @staticmethod
    def draw_muntin(panel_object):
        muntin_parameters = panel_object.muntin_parameters
        context = panel_object.context

        pattern = muntin_parameters.get('pattern', '')

        if not pattern:
            return

        context.save()

        dlo_x_offset = (panel_object.scaled_width - panel_object.scaled_dlo_width) / 2
        dlo_y_offset = (panel_object.scaled_height - panel_object.scaled_dlo_height) / 2

        context.set_source_rgba(*Colors.BLACK)
        context.set_line_width(0.5)

        dlo_width = panel_object.scaled_dlo_width
        dlo_height = panel_object.scaled_dlo_height

        x = panel_object.x + dlo_x_offset
        y = panel_object.y + dlo_y_offset

        b_offset = 0.10 * dlo_width

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
                Muntin.draw_line(context, ((x, y), (x, y + dlo_height)))

            # draw horizontal lines
            # reset x to initial value
            x = panel_object.x + dlo_x_offset

            # y co-ordinate for end of the dlo
            terminate_y = y + dlo_height

            while y < terminate_y:
                y = y + dlo_height / rows
                Muntin.draw_line(context, ((x, y), (x + dlo_width, y)))

        elif pattern in ['brittany-6', 'brittany-9']:
            Muntin.draw_line(context, ((x + b_offset, y), (x + b_offset, y + dlo_height)))
            Muntin.draw_line(context, ((x + dlo_width - b_offset, y), (x + dlo_width - b_offset, y + dlo_height)))

            Muntin.draw_line(context, ((x, y + dlo_height - b_offset), (x + dlo_width, y + dlo_height - b_offset)))

        if pattern == 'brittany-9':
            Muntin.draw_line(context, ((x, y + b_offset), (x + dlo_width, y + b_offset)))

        context.restore()
