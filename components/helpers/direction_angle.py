from enums.colors import Colors


class DirectionAngle:

    @staticmethod
    def draw(context, x, y, width, height, direction):

        context.set_dash([3, 3])
        context.set_source_rgba(*Colors.LIGHT_GREY)
        context.set_line_width(0.5)

        if direction == 'left':
            context.move_to(x + width, y)
            context.line_to(x, y + height / 2)
            context.line_to(x + width, y + height)
        elif direction == "right":
            context.move_to(x, y)
            context.line_to(x + width, y + height / 2)
            context.line_to(x, y + height)
        elif direction == "up":
            context.move_to(x, y)
            context.line_to(x + width / 2, y + height)
            context.line_to(x + width, y)
        elif direction == "down":
            context.move_to(x, y + height)
            context.line_to(x + width / 2, y)
            context.line_to(x + width, y + height)
        else:
            return

        context.stroke()
