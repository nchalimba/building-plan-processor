from dataclasses import dataclass, field

from app.main.dtos.response.point_dto import PointDto

'''
Description: This class contains the api representation of windows.
'''
@dataclass
class WindowDto:
    center_point: PointDto
    start_point: PointDto
    end_point: PointDto
    radius: float
    angle: float
    window_id: str = field(default=None)
    amount_matched: int = field(default=None)
    is_matched: bool = field(default=None)
