

'''
Description: This file contains all possible available (extractable) data per plan type.
'''

SIMPLE_PLAN = {
    "polygon": ["id", "area", "perimeter", "shape_type", "amount_corners", "has_curves", 
    "has_roomstamp", "ignored_edges_percentage", "outer_wall_percentage", "pillars", 
    "points", "adjacent_polygons", "room", "walls"],
    "unmatched_room": ["room_number", "room_type", "room_area"],
    "pillar": ["start_point", "end_point"],
    "point": ["x_coordinate", "y_coordinate"],
    "room": ["room_number", "room_type", "room_area"],
    "wall": ["is_outer_wall", "orientation", "length", "sky_direction", "start_point", "end_point"],
    "adjacent_polygon": ["polygon_id"]
}
ARCHITECTURE_PLAN = {
    "pillar": ["center_point", "radius"],
    "window": ["radius", "angle", "center_point", "start_point", "end_point"],
    "architecture_wall": ["wall_thickness", "wall_type", "lines"],
    "line": ["start_point", "end_point"],
    "point": ["x_coordinate", "y_coordinate"],
    "facade_line": ["start_point", "end_point"],
    "facade_arc": ["center_point", "start_point", "end_point", "radius", "start_angle", "end_angle", "lines"]
}

COMBINED_PLAN = {
    "simple_plan": ["orientation", "polygons", "unmatched_rooms"],
    "polygon": ["id", "area", "perimeter", "shape_type", "amount_corners", "has_curves", 
    "has_roomstamp", "ignored_edges_percentage", "outer_wall_percentage", "pillars", 
    "points", "adjacent_polygons", "room", "walls"],
    "unmatched_room": ["room_number", "room_type", "room_area"],
    "pillar": ["start_point", "end_point", "center_point", "radius", "is_matched"],
    "point": ["x_coordinate", "y_coordinate"],
    "room": ["room_number", "room_type", "room_area"],
    "adjacent_polygon": ["polygon_id"],
    "wall": ["wall_id", "is_outer_wall", "orientation", "length", "sky_direction", "start_point", "end_point", "wall_thickness", "wall_type", "window_length", "windows"],
    "window": ["window_id", "amount_matched", "is_matched", "radius", "angle", "center_point", "start_point", "end_point"],
    "architecture_plan": ["pillars", "windows", "architecture_walls"],
    "architecture_wall": ["simple_wall_ids", "wall_thickness", "wall_type", "lines"],
    "line": ["start_point", "end_point"],
    "facade_line": ["start_point", "end_point"],
    "facade_arc": ["center_point", "start_point", "end_point", "radius", "start_angle", "end_angle", "lines"]
}

