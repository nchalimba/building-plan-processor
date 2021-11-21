from dataclasses import dataclass, field

from app.main.dtos.response.polygon_dto import PolygonDto
#from app.main.dtos.response.unmatched_room_dto import Unmatched_roomDto
from app.main.dtos.response.report_dto import ReportDto
from app.main.dtos.response.room_dto import RoomDto

'''
Description: This class contains the api representation of simple plans.
'''

@dataclass
class SimplePlanDto:
    status: str
    floor: int = field(default=None)
    orientation: float = field(default=None)
    polygons: list[PolygonDto] = field(default=None)
    unmatched_rooms: list[RoomDto] = field(default=None)
    report: ReportDto = field(default=None)

