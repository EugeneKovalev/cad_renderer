from functools import cached_property

import cairo

from components.config import SLIDING_DOOR_PRODUCT_CATEGORY_ID
from components.top_view.utils import get_dimensions_from_layers, get_frames_with_panels, get_number_of_tracks_value, \
    get_track_number_of_panel, get_frame_category, get_pocket_width, get_pocket_location
from enums.colors import Colors


class TopView:
    PANEL_HEIGHT = 10
    ENFORCEMENT_SIZE = 15
    TRACK_WRAP_THICKNESS = 10
    TEXT_SIZE = 10

    def __init__(self, x=0, y=0, raw_params=None, scale_factor=1, draw_label=True):
        self._context = None
        self.parent_panel = None
        self.draw_label = draw_label

        self.x = x
        self.y = y
        self.raw_params = raw_params

        self.panel_type = raw_params['panel_type']
        self.name = raw_params['name'] if raw_params['panel_type'] == 'panel' else 'frame'

        self.scale_factor = scale_factor
        self._size_labels = []
        self.child_labels = []

    @cached_property
    def number_of_tracks(self):
        number_of_tracks = get_number_of_tracks_value(self.raw_params.get('constructor_data', {}))
        if number_of_tracks:
            return number_of_tracks
        else:
            return 0

    @cached_property
    def frame_category(self):
        frame_category = get_frame_category(self.raw_params.get('constructor_data', {}))
        if frame_category:
            return frame_category.lower()
        else:
            return ''

    @cached_property
    def pocket_location(self):
        pocket_location = get_pocket_location(self.raw_params.get('constructor_data', {}))
        if pocket_location:
            return pocket_location.lower()
        else:
            return ''

    @cached_property
    def pocket_width(self):
        pocket_width = get_pocket_width(self.raw_params.get('constructor_data', {}))
        return pocket_width

    def is_frame_sliding_assembly(self, frame_tree):
        assembly_version = frame_tree.get('assembly_version', {})
        product_category_id = assembly_version.get('product_category_id')

        if product_category_id == SLIDING_DOOR_PRODUCT_CATEGORY_ID:
            return True
        else:
            return False

    @property
    def scaled_frame_height(self):
        return 30 * self.number_of_tracks

    @property
    def width(self):
        if self.raw_params.get('height_width_2x', True):
            return self.height * 2
        else:
            return self.raw_params['width']

    @property
    def height(self):
        return self.raw_params['height']

    @property
    def dlo_width(self):
        return self.raw_params['dlo_width']

    @property
    def dlo_height(self):
        return self.raw_params['dlo_height']

    @property
    def scaled_width(self):
        if self.raw_params.get('height_width_2x', True):
            return self.scaled_height * 2
        else:
            return self.width * self.scale_factor

    @property
    def scaled_height(self):
        return self.height * self.scale_factor

    @property
    def scaled_dlo_width(self):
        return self.dlo_width * self.scale_factor

    @property
    def scaled_dlo_height(self):
        return self.dlo_height * self.scale_factor

    @property
    def size_labels(self):
        return self._size_labels

    @property
    def context(self) -> cairo.Context:
        if not self._context:
            raise NotImplementedError

        return self._context

    def set_context(self, context):
        """
        Sets a context to draw a panel onto
        """
        self._context = context
        return self

    def draw_text(self, x, y, text):
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_font_matrix(cairo.Matrix(xx=self.TEXT_SIZE, yy=-self.TEXT_SIZE))

        self.context.move_to(x, y)
        self.context.show_text(text)
        self.context.stroke()

    def draw(self):

        self.context.save()

        # add gap for pocket first
        if self.frame_category.startswith('pck'):
            self.x = self.x + self.pocket_width * self.scale_factor + 10

        self.y = self.y + (self.number_of_tracks - 1) * TopView.ENFORCEMENT_SIZE

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(2)

        constructor_data = self.raw_params.get("constructor_data", {})

        if not constructor_data:
            return

        frames = get_frames_with_panels(constructor_data)

        for frame in frames:

            # skip if its not sliding glass door
            if not self.is_frame_sliding_assembly(frame):
                continue

            frame_dimension = get_dimensions_from_layers(frame.get("layers", {}))
            # draw frame
            width = frame_dimension.get('width', 0) * self.scale_factor
            height = frame_dimension.get('height', 0) * self.scale_factor

            # Draw the panel
            # self.context.rectangle(self.x, self.y, width, self.scaled_frame_height)
            # self.context.stroke()

            # Initialize variables to track position
            x_offset = 5  # Initial x offset
            og_y_offset = (self.scaled_frame_height - 5 * (
                    self.number_of_tracks - 1) - 1.5 * TopView.ENFORCEMENT_SIZE * self.number_of_tracks) / 2  # Initial y offset

            # filter screens, normal panel will have z index as 1
            filtered_panels = [panel for panel in frame['children'] if panel['position']['z'] == 1]

            # Sort the children according to position['x']
            sorted_panels = sorted(filtered_panels, key=lambda x: x['position']['x'])

            self.context.set_line_width(1)

            # find min and max of x to draw tracks enclosure
            panel_min_x = self.x + x_offset
            panel_max_x = self.x + width / 2

            prev_track_number = self.number_of_tracks

            for panel_index, child in enumerate(sorted_panels):
                if child.get('panel_type') != 'panel':
                    continue

                track_number = self.number_of_tracks - get_track_number_of_panel(child) + 1

                if panel_index != 0 and track_number != prev_track_number:
                    x_offset = x_offset - TopView.ENFORCEMENT_SIZE - 1

                y_offset = og_y_offset + (track_number - 1) * 1.25 * TopView.ENFORCEMENT_SIZE + 2 * (
                        track_number - 1) - 1 if track_number != 1 else og_y_offset

                dimensions = get_dimensions_from_layers(child.get('layers', []))
                width = dimensions.get('width', 0) * self.scale_factor
                height = dimensions.get('height', 0) * self.scale_factor

                # draw panel name
                self.draw_text(self.x + x_offset + width / 2 - 16,
                               self.y + self.number_of_tracks * 2.5 * TopView.PANEL_HEIGHT,
                               f'Panel {child.get("name", "").upper()}')

                # Draw the start enforcement square
                self.context.rectangle(self.x + x_offset, self.y + y_offset - 2, TopView.ENFORCEMENT_SIZE,
                                       TopView.ENFORCEMENT_SIZE)

                # Draw the panel
                self.context.rectangle(self.x + x_offset + TopView.ENFORCEMENT_SIZE, self.y + y_offset + 1,
                                       width - 2 * TopView.ENFORCEMENT_SIZE, TopView.PANEL_HEIGHT)

                # Draw the end enforcement square
                self.context.rectangle(self.x + x_offset + width - TopView.ENFORCEMENT_SIZE, self.y + y_offset - 2,
                                       TopView.ENFORCEMENT_SIZE, TopView.ENFORCEMENT_SIZE)
                self.context.stroke()

                # check max x
                new_max_x = self.x + x_offset + width
                panel_max_x = max(new_max_x, panel_max_x)

                x_offset += width + 1.5

                prev_track_number = track_number

            self.context.set_line_width(2)

            track_y = self.y + og_y_offset - 0.3 * TopView.ENFORCEMENT_SIZE

            # draw exterior and interior
            text_start_x = (panel_min_x + panel_max_x) / 2 - 18
            self.draw_text(text_start_x, self.y + self.number_of_tracks * 2.5 * TopView.PANEL_HEIGHT + 20, 'INTERIOR')
            self.draw_text(text_start_x, self.y - 20, 'EXTERIOR')

            # draw track extremes
            first_track_y = None
            last_track_y = track_y
            for track_index in range(self.number_of_tracks):
                # write track number
                if not self.frame_category.startswith('pck') and not self.frame_category.endswith('pck'):
                    self.draw_text(panel_min_x - 45, track_y + 7.5, f'Track {self.number_of_tracks - track_index}')

                if not self.frame_category.startswith('pck'):
                    self.context.move_to(panel_min_x + TopView.TRACK_WRAP_THICKNESS, track_y)
                    self.context.line_to(panel_min_x, track_y)
                    self.context.line_to(panel_min_x, track_y + 2 * TopView.PANEL_HEIGHT + 1)
                    self.context.line_to(panel_min_x + TopView.TRACK_WRAP_THICKNESS,
                                         track_y + 2 * TopView.PANEL_HEIGHT + 1)

                if not self.frame_category.endswith('pck'):
                    self.context.move_to(panel_max_x - TopView.TRACK_WRAP_THICKNESS, track_y)
                    self.context.line_to(panel_max_x, track_y)
                    self.context.line_to(panel_max_x, track_y + 2 * TopView.PANEL_HEIGHT + 1)
                    self.context.line_to(panel_max_x - TopView.TRACK_WRAP_THICKNESS,
                                         track_y + 2 * TopView.PANEL_HEIGHT + 1)

                self.context.stroke()

                first_track_y = track_y
                track_y = track_y + 1.25 * TopView.ENFORCEMENT_SIZE + 1

            # draw pocket on right side 'STD-PCK' or 'PCK-PCK'
            if self.frame_category.endswith('pck') and first_track_y:
                rect_x = panel_max_x
                # if pocket location is exterior, draw inside above first track else below last track
                if self.pocket_location == 'out':
                    rect_y = first_track_y + 2 * TopView.PANEL_HEIGHT
                else:
                    rect_y = last_track_y - 2 * TopView.PANEL_HEIGHT

                rect_width, rect_height = int(
                    self.pocket_width) * self.scale_factor, 2 * TopView.PANEL_HEIGHT  # Rectangle size

                self.draw_text(panel_max_x + rect_width / 2 - 20,
                               self.y + self.number_of_tracks * 2.5 * TopView.PANEL_HEIGHT + 20,
                               'POCKET')

                self.draw_pocket(rect_x, rect_y, rect_width, rect_height)

                # draw inner part
                self.context.set_line_width(2)
                if self.pocket_location == 'out':
                    inner_part_y = rect_y
                else:
                    inner_part_y = rect_y - 0.75 * TopView.PANEL_HEIGHT
                self.context.rectangle(rect_x - TopView.TRACK_WRAP_THICKNESS, inner_part_y,
                                       TopView.TRACK_WRAP_THICKNESS, 2.75 * TopView.PANEL_HEIGHT)
                self.context.stroke()

            # draw pocket on left side 'PCK-PCK' or 'PCK-STD'
            if self.frame_category.startswith('pck') and first_track_y:
                # if pocket location is exterior, draw inside above first track else below last track
                if self.pocket_location == 'out':
                    rect_y = first_track_y + 2 * TopView.PANEL_HEIGHT
                else:
                    rect_y = last_track_y - 2 * TopView.PANEL_HEIGHT

                rect_width, rect_height = int(
                    self.pocket_width) * self.scale_factor, 2 * TopView.PANEL_HEIGHT  # Rectangle size

                rect_x = panel_min_x - rect_width

                self.draw_text(rect_x + rect_width / 2 - 20,
                               self.y + self.number_of_tracks * 2.5 * TopView.PANEL_HEIGHT + 20,
                               'POCKET')

                self.draw_pocket(rect_x, rect_y, rect_width, rect_height)

                # draw inner part
                self.context.set_line_width(2)
                if self.pocket_location == 'out':
                    inner_part_y = rect_y
                else:
                    inner_part_y = rect_y - 0.75 * TopView.PANEL_HEIGHT
                self.context.rectangle(rect_x + rect_width, inner_part_y,
                                       TopView.TRACK_WRAP_THICKNESS, 2.75 * TopView.PANEL_HEIGHT)
                self.context.stroke()

            # draw only one frame
            break

        self.context.restore()

    def draw_pocket(self, rect_x, rect_y, rect_width, rect_height):
        """
        Draw pocket with tilted lines inside it
        """

        self.context.rectangle(rect_x, rect_y, rect_width, rect_height)

        # Set the rectangle border color and fill
        self.context.set_line_width(1)
        self.context.stroke()

        # Apply the rectangle as a clipping region
        self.context.rectangle(rect_x, rect_y, rect_width, rect_height)
        self.context.clip()

        # Set shading line properties
        self.context.set_source_rgb(0.3, 0.3, 0.3)  # Gray color for shading

        # Draw tilted (diagonal) lines inside the rectangle
        spacing = 5  # Space between each line
        for offset in range(0, rect_width + rect_height, spacing):
            self.context.move_to(rect_x + offset, rect_y)
            self.context.line_to(rect_x, rect_y + offset)
            self.context.stroke()

        self.context.reset_clip()
        self.context.set_source_rgb(0, 0, 0)  # Gray color for shading
