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

    if 'children' in json_data:
        # Iterate through each child item
        for child in json_data['children']:
            # Check if the child is a frame
            if child.get('panel_type') == 'frame':
                # Check if the frame has at least one panel
                if any(sub_child.get('panel_type') == 'panel' for sub_child in child.get('children', [])):
                    frames_with_panels.append(child)
                else:
                    # If the frame doesn't have panels, recursively check its children frames
                    frames_with_panels.extend(get_frames_with_panels(child))

    return frames_with_panels


def get_number_of_tracks_value(tree):
    for child in tree.get('children', []):
        # Check if the child is a frame
        if child.get('panel_type') != 'frame':
            continue

        for parameter in child.get("parameters", []):
            if parameter.get("name") == NUMBER_OF_TRACKS_PARAM_NAME:
                try:
                    return int(parameter.get("value_name"))
                except:
                    pass

        for inner_child in tree.get('children', []):
            tracks = get_number_of_tracks_value(inner_child)
            if tracks:
                return tracks

    return None


def get_track_number_of_panel(panel):
    for parameter in panel.get("parameters", []):
        if parameter.get("name") == TRACK_NUMBER_PARAM_NAME:
            try:
                return int(parameter.get("value_name"))
            except:
                pass

    return 1
