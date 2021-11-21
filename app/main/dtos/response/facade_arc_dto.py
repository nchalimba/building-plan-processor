from dataclasses import dataclass, field

from app.main.dtos.response.line_dto import LineDto
from app.main.dtos.response.point_dto import PointDto

'''
Description: This class contains the api representation of facade arcs.
'''

@dataclass
class FacadeArcDto:
    center_point: PointDto
    start_point: PointDto
    end_point: PointDto
    radius: float
    start_angle: float
    end_angle: float
    lines: list[LineDto] = field(default=None)
