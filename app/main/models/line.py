from dataclasses import dataclass, field

from app.main.dtos.response.line_dto import LineDto
from shapely.geometry import linestring

from .point import Point

''' 
    Description: This class represents a line in order to match walls.
'''


@dataclass()
class Line:
    id_wall: str = field(default=None)
    line_string: linestring = field(default=None)
    start_point: Point = field(default=None)
    end_point: Point = field(default=None)
    
    def convert_to_dto(self) -> LineDto:
        '''
        Description: This method transforms a line to its dto representation.
        Params: self: Line
        Return: line_dto: LineDto
        '''

        start_point_dto = self.start_point.convert_to_dto()
        end_point_dto = self.end_point.convert_to_dto()
        return LineDto(start_point_dto, end_point_dto)
    