from dataclasses import dataclass, field

from app.main.dtos.response.point_dto import PointDto
from app.main.dtos.response.window_dto import WindowDto

'''
Description: This class contains the api representation of adjacent walls.
'''

@dataclass
class WallDto:
    start_point: PointDto
    end_point: PointDto
    length: float = field(default=None)
    is_outer_wall: bool = field(default=False)
    is_pillar: bool = field(default=False)
    orientation: float = field(default=None)
    wall_thickness: float = field(default=None)
    window_length: float = field(default=None)
    wall_type: str = field(default=None)
    sky_direction: str = field(default=None)
    wall_id: str = field(default=None)
    windows: list[WindowDto] = field(default=None)
    
