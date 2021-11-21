from dataclasses import dataclass, field

from app.main.dtos.response.facade_arc_dto import FacadeArcDto
from app.main.models.line import Line
from app.main.models.point import Point

'''
Description: This class represents a facade arc in an architecture plan.
'''
@dataclass
class FacadeArc:
    center_point: Point
    start_point: Point
    end_point: Point
    radius: float
    start_angle: float
    end_angle: float
    lines: list[Line] = field(default=None)
    perimeter: float = field(default=None)
    delta_angle: float = field(default=None)
    line_count: int = field(default=None)
    
    def convert_to_dto(self) -> FacadeArcDto:
        '''
        Description: This method transforms a facade arc to its dto representation.
        Params: self: FacadeArc
        Return: facade_arc_dto: FacadeArcDto
        '''
        
        line_dtos = None
        if self.lines:
            line_dtos = []
            for line in self.lines:
                line_dtos.append(line.convert_to_dto())
        return FacadeArcDto(self.center_point.convert_to_dto(), self.start_point.convert_to_dto(), self.end_point.convert_to_dto(),
            self.radius, self.start_angle, self.end_angle, line_dtos)
