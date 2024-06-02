class Arrow:
    WIDTH = 20
    HEIGHT = 12
    def __init__(self, width=20, height=12):
        self.width = max(width, Arrow.WIDTH)
        self.height = max(height, Arrow.HEIGHT)

    def draw(self, context, x, y, direction):

        if direction in ['top', 'down']:
            height = self.width
            width = self.height
        else:
            width = self.width
            height = self.height

        x = x - width / 2
        y = y - height / 2

        a, b = width * 0.6, height*0.7

        context.set_line_width(1)

        if direction == 'right':
            points = [
                (x, y + b),
                (x, y + height - b),
                (x + a, y + height - b),
                (x + a, y + height),
                (x + width, y + height / 2),
                (x + a, y),
                (x + a, y + b),
                (x, y + b)
            ]
        elif direction == "left":

            points = [
                (x + width, y + b),
                (x + width, y + height - b),
                (x + width - a, y + height - b),
                (x + width - a, y + height),
                (x, y + height / 2),
                (x + width - a, y),
                (x + width - a, y + b),
                (x + width, y + b)
            ]

        elif direction == "top":

            points = [
                (x + b, y),
                (x + width - b, y),
                (x + width - b, y + a),
                (x + width, y + a),
                (x + width / 2, y + height),
                (x, y + a),
                (x + b, y + a),
                (x + b, y)
            ]

        elif direction == "down":

            points = [
                (x + b, y + height),
                (x + width - b, y + height),
                (x + width - b, y + height - a),
                (x + width, y + height - a),
                (x + width / 2, y),
                (x, y + height - a),
                (x + b, y + height - a),
                (x + b, y + height)
            ]
        else:
            return

        # Move to the starting point
        context.move_to(*points[0])

        # Loop through the points array to draw the lines
        for point in points[1:]:
            context.line_to(*point)

        context.stroke()
