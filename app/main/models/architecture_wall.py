from dataclasses import dataclass, field

from app.main.dtos.response.architecture_wall_dto import ArchitectureWallDto
from ezdxf.entities.lwpolyline import LWPolyline

from .line import Line

''' 
    Description: This class represents a wall in a polygon or architecture plan.
'''


@dataclass()
class Architecture_Wall:
    id: str
    polyline: LWPolyline
    wall_thickness: float = field(default=None)
    wall_type: str = field(default=None)
    lines: list[Line] = field(default=None)
    simple_wall_ids: list[str] = field(default=None)

    def convert_to_dto(self) -> ArchitectureWallDto:
        '''
        Description: This method transforms an architecture wall to its dto representation.
        Params: self: Architecture_Wall
        Return: architecture_wall_dto: ArchitectureWallDto
        '''
        
        line_dtos = None
        if self.lines:
            line_dtos = []
            for line in self.lines:
                line_dtos.append(line.convert_to_dto())
        return ArchitectureWallDto(self.wall_thickness, self.wall_type, line_dtos, self.simple_wall_ids)
