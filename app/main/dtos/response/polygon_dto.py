from dataclasses import dataclass, field, fields

from app.main.dtos.response.adjacent_polygon_dto import AdjacentPolygonDto
from app.main.dtos.response.pillar_dto import PillarDto
from app.main.dtos.response.point_dto import PointDto
from app.main.dtos.response.room_dto import RoomDto
from app.main.dtos.response.wall_dto import WallDto

'''
Description: This class contains the api representation of polygons.
'''

@dataclass
class PolygonDto:
    id: int
    area: float
    perimeter: float
    has_roomstamp: bool = field(default=False)
    points: list[PointDto] = field(default=None)
    room: RoomDto = field(default=None)
    adjacent_polygons: list[AdjacentPolygonDto] = field(
        default=None)
    walls: list[WallDto] = field(default=None)

    jetty_area: float = field(default=None)
    has_jetty: bool = field(default=True)
    amount_corners: int = field(default=0)
    has_curves: bool = field(default=False)
    shape_type: str = field(default=None)
    outer_wall_percentage: float = field(default=None)
    ignored_edges_percentage: float = field(default=0.0)
    pillars: list[PillarDto] = field(default=None)
    geometry: str = field(default=None)
    window_length: float = field(default=None)
    window_area: float = field(default=None)
    facade_length: float = field(default=None)
    facade_area: float = field(default=None)

