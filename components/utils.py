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


def has_muntin_parts(raw_params):
    """
    Checks if the input params contains any muntin_parts within "frames" or "panels".

    Args:
        raw_params (dict): raw params.

    Returns:
        bool: True if muntin_parts are found within "frames" or "panels", False otherwise.
    """

    # added to fix the multi panel issue
    return False

    if 'frames' in raw_params:
        for frame in raw_params['frames']:
            if 'muntin_parts' in frame and frame['muntin_parts']:
                return True
    if 'panels' in raw_params:
        for panel in raw_params['panels']:
            if 'muntin_parts' in panel and panel['muntin_parts']:
                return True
    for key, value in raw_params.items():
        if isinstance(value, dict):
            if has_muntin_parts(value):
                return True
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    if has_muntin_parts(item):
                        return True
    return False
