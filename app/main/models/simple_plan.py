from dataclasses import dataclass, field

from app.main.dtos.response.room_dto import RoomDto
from app.main.dtos.response.simple_plan_dto import SimplePlanDto
from app.main.models.room import Room
from loguru import logger

from .polygon import Polygon

main_logger = logger.bind()

'''
    @Description: This class represents an simple plan, 
    which contains a roomstamp for every polygon. 
    Polygons are generally extracted through a simple plan.
'''


@dataclass()
class Simple_Plan:
    file_name: str
    file_path: str
    floor_height: float
    orientation: float
    status: str = field(default=None)
    floor: int = field(default=None)
    polygons: list[Polygon] = field(default=None)
    unmatched_rooms: list[Room] = field(default=None)

    def convert_to_dto(self, floor_height: float = None) -> SimplePlanDto:
        '''
        Description: This method transforms a simple plan to its dto representation.
        Params: self: Simple_Plan, floor_height: float
        Return: simple_plan_dto: SimplePlanDto
        '''

        polygon_dtos = None
        if self.polygons:
            polygon_dtos = []
            for polygon in self.polygons:
                polygon_dtos.append(polygon.convert_to_dto(floor_height))

        if self.unmatched_rooms:
            unmatched_room_dtos = []
            for x in self.unmatched_rooms:
                unmatched_room = RoomDto(self.convert_area_to_float(x[2][1]), x[0][1], x[1][1])
                unmatched_room_dtos.append(unmatched_room)
        else:
            unmatched_room_dtos = None
        return SimplePlanDto(self.status, floor=self.floor, orientation=self.orientation,
                             polygons=polygon_dtos, unmatched_rooms=unmatched_room_dtos)

    def convert_area_to_float(self, area: str) -> float:
        '''
        Description: This method parses an area into a float
        Params: area: str
        Return: area: float
        '''
        area = area.replace(",", ".")
        area = area[:-3]
        try:
            area = float(area)
        except Exception as e:
            area = 0.0
            main_logger.error(str(e))
        return area
