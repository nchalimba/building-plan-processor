from dataclasses import dataclass, field

from app.main.dtos.response.architecture_plan_dto import ArchitecturePlanDto
from app.main.models.facade_arc import FacadeArc
from app.main.models.line import Line

from .architecture_wall import Architecture_Wall
from .pillar import Pillar
from .polygon import Polygon
from .wall import Wall
from .window import Window

''' 
    Description: This class represents an architecture plan, which contains further information about a building.
'''
@dataclass()
class Architecture_Plan:
    file_name: str
    file_path: str
    floor_height: float
    architecture_walls: list[Architecture_Wall]
    pillars: list[Pillar]
    windows: list[Window]
    facade_lines: list[Line]
    facade_arcs: list[FacadeArc] = field(default=None)

    def convert_to_dto(self) -> ArchitecturePlanDto:
        '''
        Description: This method transforms an architecture plan to its dto representation.
        Params: self: Architecture_Plan
        Return: architecture_plan_dto: ArchitecturePlanDto
        '''

        facade_arc_dtos = None
        if self.facade_arcs:
            facade_arc_dtos = []
            for facade_arc in self.facade_arcs:
                facade_arc_dtos.append(facade_arc.convert_to_dto())
        pillar_dtos = []
        for pillar in self.pillars:
            pillar_dtos.append(pillar.convert_to_dto())
        window_dtos = []
        for window in self.windows:
            window_dtos.append(window.convert_to_dict())
        architecture_wall_dtos = None
        if self.architecture_walls:
            architecture_wall_dtos = []
            for architecture_wall in self.architecture_walls:
                architecture_wall_dtos.append(architecture_wall.convert_to_dto())
        facade_line_dtos = []
        for facade_line in self.facade_lines:
            facade_line_dtos.append(facade_line.convert_to_dto())
        return ArchitecturePlanDto(pillar_dtos, window_dtos, architecture_wall_dtos, facade_line_dtos, facade_arcs=facade_arc_dtos)
