from dataclasses import dataclass, field

from app.main.dtos.response.point_dto import PointDto

'''
    Description: This class represents a coordinate point.
'''


@dataclass()
class Point:
    x_coordinate: float
    y_coordinate: float
    s_width: float = field(default=None)
    e_width: float = field(default=None)
    b_value: float = field(default=None)

    def convert_to_dto(self) -> PointDto:
        '''
        Description: This method transforms a point to its dto representation.
        Params: self: Point
        Return: point_dto: PointDto
        '''
        
        x_coordinate_dto = self.x_coordinate
        y_coordinate_dto = self.y_coordinate
        return PointDto(x_coordinate_dto, y_coordinate_dto)
