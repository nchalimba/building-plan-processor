from dataclasses import dataclass, field

from app.main.dtos.response.architecture_wall_dto import ArchitectureWallDto
from app.main.dtos.response.facade_arc_dto import FacadeArcDto
from app.main.dtos.response.line_dto import LineDto
from app.main.dtos.response.pillar_dto import PillarDto
from app.main.dtos.response.window_dto import WindowDto
from app.main.models.line import Line

'''
Description: This class contains the api representation of architecture plans.
'''

@dataclass
class ArchitecturePlanDto:
    pillars: list[PillarDto]
    windows: list[WindowDto]
    architecture_walls: list[ArchitectureWallDto]
    facade_lines: list[LineDto]
    facade_arcs: list[FacadeArcDto] = field(default=None)

