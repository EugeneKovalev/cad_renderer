from components.config import *


def get_dimensions_from_layers(layers):
    dimensions = {}
    for layer in layers:
        if layer.get('main', False):
            dimensions = layer.get('dimensions', {})
            break
    return dimensions


def get_frames_with_panels(json_data):
    frames_with_panels = []

    def check_child(child):
        # Check if the child is a frame
        if child.get('panel_type') == 'frame':
            # Check if the frame has at least one panel
            if any(sub_child.get('panel_type') == 'panel' for sub_child in child.get('children', [])):
                frames_with_panels.append(child)
            else:
                # If the frame doesn't have panels, recursively check its children frames
                frames_with_panels.extend(get_frames_with_panels(child))
        elif child.get('panel_type') in ['subunit', 'unit']:
            # If the child is a subunit or unit, perform a recursive check
            for sub_child in child.get('children', []):
                check_child(sub_child)

    # Iterate through each child item
    for child in json_data.get('children', []):
        check_child(child)

    return frames_with_panels


def get_pocket_width(tree):
    try:
        min_width = 99999999
        frames = get_frames_with_panels(tree)
        panel_found = False

        for frame in frames:
            for panel in frame.get('children', []):
                dimension = get_dimensions_from_layers(panel.get('layers', []))
                width = dimension.get('width', 0)
                min_width = min(min_width, width)
                panel_found = True

        if not panel_found:
            return 20
    except:
        min_width = 20

    return min_width


def get_frame_parameter_value(tree, parameter_name):
    parameter_value = None

    def check_child(child):
        nonlocal parameter_value
        if child.get('panel_type') == 'frame':
            # Iterate through parameters
            for parameter in child.get('parameters', []):
                # Check if parameter name is "number of tracks"
                if parameter.get('name') == parameter_name:
                    try:
                        parameter_value = parameter.get('value_name', None)
                        return  # Exit the loop once the value is found
                    except ValueError:
                        # Ignore error
                        pass
        elif child.get('panel_type') in ['subunit', 'unit']:
            # If the child is a subunit or unit, perform a recursive check
            for sub_child in child.get('children', []):
                check_child(sub_child)
                if parameter_value:
                    return

    for child in tree.get('children', []):
        check_child(child)
        if parameter_value:
            break

    return parameter_value


def get_number_of_tracks_value(tree):
    val = get_frame_parameter_value(tree, NUMBER_OF_TRACKS_PARAM_NAME)
    if not val:
        return 0

    return int(val)


def get_frame_category(tree):
    val = get_frame_parameter_value(tree, FRAME_CATEGORY_PARAM_NAME)

    return val


def get_pocket_location(tree):
    val = get_frame_parameter_value(tree, POCKET_LOCATION_PARAM_NAME)

    return val


def get_pull_type(tree) -> str:
    val = get_frame_parameter_value(tree, PULL_TYPE_PARAM_NAME)

    return val


def get_panel_parameter_value(panel, param_name):
    """
    Searches the panel's 'parameters' for the given param_name.
    Returns the parameter's 'value_name' if found, otherwise None.
    """
    for parameter in panel.raw_params.get("parameters", []):
        if parameter.get("name").lower() == param_name.lower():
            return parameter.get("value_name").lower()
    return None

def get_track_number_of_panel(panel):
    """
    Uses the helper get_panel_parameter_value to find the track_number parameter.
    If it can be converted to int, returns it; otherwise defaults to 1.
    """
    value = get_panel_parameter_value(panel, TRACK_NUMBER_PARAM_NAME)
    if value is not None:
        try:
            return int(value)
        except ValueError:
            pass
    return 1

def get_pull_handle_location(tree, panel) -> str:
    """
    Looks for the pull handle location in the panel's parameters first.
    If not found there, attempts to get it from the tree.
    """
    # Try the panel first
    val = get_panel_parameter_value(panel, PULL_HANDLE_LOCATION_PARAM_NAME)
    if val is not None:
        return val

    # Fallback to the frame parameters in the tree
    val = get_frame_parameter_value(tree, PULL_HANDLE_LOCATION_PARAM_NAME)
    return val

