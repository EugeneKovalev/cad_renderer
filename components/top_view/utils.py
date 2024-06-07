from components.config import NUMBER_OF_TRACKS_PARAM_NAME, TRACK_NUMBER_PARAM_NAME


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


def get_number_of_tracks_value(tree):
    number_of_tracks = 0

    def check_child(child):
        nonlocal number_of_tracks
        if child.get('panel_type') == 'frame':
            # Iterate through parameters
            for parameter in child.get('parameters', []):
                # Check if parameter name is "number of tracks"
                if parameter.get('name') == NUMBER_OF_TRACKS_PARAM_NAME:
                    try:
                        number_of_tracks = int(parameter.get('value_name', 0))
                        return  # Exit the loop once the value is found
                    except ValueError:
                        # Ignore error
                        pass
        elif child.get('panel_type') in ['subunit', 'unit']:
            # If the child is a subunit or unit, perform a recursive check
            for sub_child in child.get('children', []):
                check_child(sub_child)
                if number_of_tracks:
                    return

    for child in tree.get('children', []):
        check_child(child)
        if number_of_tracks:
            break

    return number_of_tracks


def get_track_number_of_panel(panel):
    for parameter in panel.get("parameters", []):
        if parameter.get("name") == TRACK_NUMBER_PARAM_NAME:
            try:
                return int(parameter.get("value_name"))
            except:
                pass

    return 1
