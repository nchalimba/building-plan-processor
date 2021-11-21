from dataclasses import dataclass, field

from app.main.dtos.response.pillar_dto import PillarDto
from app.main.models.line import Line
from app.main.models.point import Point

'''
Description: This class represents a pillar in an architecture plan or simple plan.
'''

@dataclass
class Pillar:
    start_point: Point = field(default=None)
    end_point: Point = field(default=None)
    center_point: Point = field(default=None)
    radius: float = field(default=None)
    pillar_id: str = field(default=None)
    is_matched: bool = field(default=False)
    lines: list[Line] = field(default=None)
    points: list[Point] = field(default=None)

    def convert_to_dto(self) -> PillarDto:
        '''
        Description: This method transforms a line to its dto representation.
        Params: self: Pillar
        Return: pillar_dto: PillarDto
        '''
        
        start_point_dto = None
        end_point_dto = None
        center_point_dto = None
        radius = self.radius
        if self.start_point:
            start_point_dto = self.start_point.convert_to_dto()
        if self.end_point:
            end_point_dto = self.end_point.convert_to_dto()
        if self.center_point:
            center_point_dto = self.center_point.convert_to_dto()
        line_dtos = None
        if self.lines:
            line_dtos = []
            for line in self.lines:
                line_dtos.append(line.convert_to_dto())
        return PillarDto(start_point=start_point_dto, end_point=end_point_dto, 
            center_point=center_point_dto, radius=radius, is_matched=self.is_matched, lines=line_dtos)

