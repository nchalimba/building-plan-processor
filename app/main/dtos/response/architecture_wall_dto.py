from dataclasses import dataclass, field

from app.main.dtos.response.line_dto import LineDto

'''
Description: This class contains the api representation of architecture walls.
'''

@dataclass
class ArchitectureWallDto:
    wall_thickness: float
    wall_type: str
    lines: list[LineDto]
    simple_wall_ids: list[str] = field(default=None)
    