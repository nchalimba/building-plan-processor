from dataclasses import dataclass, field

from app.main.dtos.response.room_dto import RoomDto
from loguru import logger

main_logger = logger.bind()

'''
    Description: This class represents metadata about a polygon for a specific room. 
'''


@dataclass()
class Room:
    room_area: float
    room_perimeter: float
    room_number: str
    room_type: str
    polygon_id: str
    entity_handle: str = field(default=None)
    room_name: str = field(default=None)

    def convert_to_dto(self) -> RoomDto:
        '''
        Description: This method transforms a room to its dto representation.
        Params: self: Room
        Return: room_dto: RoomDto
        '''

        room_area = self.room_area.replace(",", ".")
        room_area = room_area[:-3]
        try:
            room_area = float(room_area)
        except Exception as e:
            room_area = 0.0
            main_logger.error(str(e))
        return RoomDto(self.room_area, self.room_number, self.room_type, room_name=self.room_name)
    

