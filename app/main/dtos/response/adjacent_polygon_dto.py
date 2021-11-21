from dataclasses import dataclass, field

'''
Description: This class contains the api representation of adjacent polygons.
'''


@dataclass
class AdjacentPolygonDto:
    adjacent_polygon_id: int
    shared_wall_length: float = field(default=None)
