import math
from components.config import PANEL_DIRECTION_PARAM_NAME

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


def find_muntin_label_offset_multipliers(raw_params):
    """
    Adds muntin_label_offset_multiplier_x and muntin_label_offset_multiplier_y attributes to 'panels' with more
    than one muntin_part levels. to handle labels for muntins in multiple panels

    It also returns the max x and y offset to calculate extra padding needed for the canvas frame

    Args:
        raw_params (dict): JSON data.

    Returns:
        dict: JSON data with added attributes 'muntin_label_offset_multiplier_y' and 'muntin_label_offset_multiplier_x'.
        max_labels_x: count of labels on x axis
        max_labels_y = count of labels on y axis
    """
    max_labels_x = 1
    max_labels_y = 1

    def process_frame(frame):

        def calculate_rank_x(panel, prev_coord):
            nonlocal max_labels_x
            nonlocal rank_x

            if panel['coordinates']['x'] > prev_coord:
                rank_x += 1

                if rank_x > max_labels_x:
                    max_labels_x = rank_x

            return rank_x

        def calculate_rank_y(panel, prev_coord):
            nonlocal max_labels_y
            nonlocal rank_y
            if panel['coordinates']['y'] > prev_coord:
                rank_y += 1

                if rank_y > max_labels_y:
                    max_labels_y = rank_y
            return rank_y

        if 'panels' in frame:
            frame['panels'] = sorted(frame['panels'], key=lambda x: x['coordinates']['x'])
            prev_x = 0
            rank_x = 0
            for panel in frame['panels']:
                if 'muntin_parts' in panel and len(panel['muntin_parts']) > 1:
                    rank_x = calculate_rank_x(panel, prev_x)
                    panel['muntin_label_offset_multiplier_x'] = rank_x
                    prev_x = panel['coordinates']['x']

            frame['panels'] = sorted(frame['panels'], key=lambda x: x['coordinates']['y'])
            prev_y = 0
            rank_y = 0
            for panel in frame['panels']:
                if 'muntin_parts' in panel and len(panel['muntin_parts']) > 1:
                    rank_y = calculate_rank_y(panel, prev_y)
                    panel['muntin_label_offset_multiplier_y'] = rank_y
                    prev_y = panel['coordinates']['y']

        for inner_frame in frame.get('frames', []):
            process_frame(inner_frame)

        return frame

    for frame in raw_params.get('frames', []):
        process_frame(frame)

    process_frame(raw_params)

    return max_labels_x, max_labels_y


def get_panel_direction_from_tree(tree, panel_name):
    for child in tree.get('children', []):
        # Check if the child is a frame
        if child.get('name') == panel_name:
            for parameter in child.get("parameters", []):
                if parameter.get("name") == PANEL_DIRECTION_PARAM_NAME:
                    try:
                        return parameter.get("value_name")
                    except:
                        pass
        else:
            for inner_child in tree.get('children', []):
                direction = get_panel_direction_from_tree(inner_child, panel_name)
                if direction:
                    return direction

    return None

def find_max_x_y_from_sides(sides):
    max_x = float('-inf')
    max_y = float('-inf')

    for side in sides:
        points = [side['start_point'], side['end_point']]
        for x, y in points:
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y

    return max_x, max_y