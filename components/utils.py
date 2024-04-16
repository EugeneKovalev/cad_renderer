import math


def find_asin(value):
    """
    Compute arcsin if value is between -1 and 1, otherwise clamp it to -1 or 1.
    There are cases where the value us 1.0000000000002 and rounding might not work as intended always, so this
    function will handle it

    Args:
    value (float): The input value

    Returns:
    float: The arcsin of the input value if it's between -1 and 1, otherwise -1 or 1.
    """
    if value <= -1:
        return -math.pi / 2  # arcsin(-1) = -pi/2
    elif value >= 1:
        return math.pi / 2  # arcsin(1) = pi/2
    else:
        return math.asin(value)
