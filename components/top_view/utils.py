from components.config import *
import logging

# Configure logging - you can adjust the level as needed
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


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


def get_frame_parameter_value(tree, param_name):
    """
    Recursively searches for a parameter within the tree.
    """
    logging.debug(f"get_frame_parameter_value called with tree: {tree}, param_name: {param_name}")

    if isinstance(tree, dict):
        if "parameters" in tree:
            for parameter in tree["parameters"]:
                if parameter.get("name", "").lower() == param_name.lower():
                    value_name = parameter.get("value_name")
                    logging.debug(f"Found value in tree parameters: {value_name}")
                    return value_name

        for key, value in tree.items():
            if isinstance(value, (dict, list)):
                result = get_frame_parameter_value(value, param_name)
                if result:
                    return result

    elif isinstance(tree, list):
        for item in tree:
            result = get_frame_parameter_value(item, param_name)
            if result:
                return result

    logging.debug(f"Value not found for {param_name}")
    return None


def get_pull_type(tree) -> str:
    logging.debug(f"get_pull_type called with tree: {tree}")
    val = get_frame_parameter_value(tree, PULL_TYPE_PARAM_NAME)
    logging.debug(f"get_pull_type returning: {val}")
    return val


def get_panel_parameter_value(panel, param_name):
    """
    Recursively searches the panel's 'parameters' and children for the given param_name.
    Returns the parameter's 'value_name' if found, otherwise None.
    """
    logging.debug(f"get_panel_parameter_value called with panel: {panel}, param_name: {param_name}")

    if isinstance(panel, dict):
        if "parameters" in panel:
            for parameter in panel.get("parameters", []):
                logging.debug(f"  Checking parameter: {parameter.get('name')}")
                if parameter.get("name", "").lower() == param_name.lower():
                    value_name = parameter.get("value_name", "").lower()
                    logging.debug(f"  Found matching parameter! value_name: {value_name}")
                    return value_name

        # Recursively check in children
        if "children" in panel:
            for child in panel.get("children", []):
                result = get_panel_parameter_value(child, param_name)
                if result:
                    return result

    elif isinstance(panel, list):
        for item in panel:
            result = get_panel_parameter_value(item, param_name)
            if result:
                return result

    logging.debug(f"  No matching parameter found for {param_name} in panel.")
    return None


def get_track_number_of_panel(panel):
    """
    Uses the helper get_panel_parameter_value to find the track_number parameter.
    If it can be converted to int, returns it; otherwise defaults to 1.
    """
    logging.debug(f"get_track_number_of_panel called with panel: {panel}")
    value = get_panel_parameter_value(panel, TRACK_NUMBER_PARAM_NAME)
    if value is not None:
        logging.debug(f"  Found track_number value: {value}")
        try:
            int_value = int(value)
            logging.debug(f"  Successfully converted to int: {int_value}")
            return int_value
        except ValueError:
            logging.debug(f"  Could not convert '{value}' to int. Returning default value 1.")
            pass
    else:
        logging.debug(f"  track_number parameter not found. Returning default value 1.")
    return 1


def get_pull_handle_location(tree, panel) -> str:
    """
    Looks for the pull handle location in the panel's parameters first.
    If not found there, attempts to get it from the tree.
    """
    logging.debug(f"get_pull_handle_location called with tree: {tree}, panel: {panel}")
    # Try the panel first
    val = get_panel_parameter_value(panel, PULL_HANDLE_LOCATION_PARAM_NAME)
    if val is not None:
        logging.debug(f"  Found pull_handle_location in panel parameters: {val}")
        return val

    # Fallback to the frame parameters in the tree
    logging.debug("  pull_handle_location not found in panel, checking tree...")
    val = get_frame_parameter_value(tree, PULL_HANDLE_LOCATION_PARAM_NAME)
    logging.debug(f"get_pull_handle_location returning from tree: {val}")
    return val
