from dataclasses import dataclass, field

from app.main.dtos.response.line_dto import LineDto
from app.main.dtos.response.point_dto import PointDto

'''
Description: This class contains the api representation of pillars.
'''
@dataclass
class PillarDto:
    start_point: PointDto = field(default=None)
    end_point: PointDto = field(default=None)
    center_point: PointDto = field(default=None)
    radius: float = field(default=None)
    is_matched: bool = field(default=None)
    lines: list[LineDto] = field(default=None)
