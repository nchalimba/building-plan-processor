from dataclasses import dataclass, field

from app.main.dtos.response.window_dto import WindowDto
from app.main.models.point import Point

''' 
Description: This class represents a window in an architecture plan or matched simple plan.
'''


@dataclass
class Window:
    window_id: str
    center_point: Point
    start_point: Point
    end_point: Point
    radius: float
    angle: float
    is_matched: bool = field(default=False)
    amount_matched: int = field(default=0)
    min_wall_distance: float = field(default=None)

    def convert_to_dict(self) -> WindowDto:
        '''
        Description: This method transforms a window to its dto representation.
        Params: self: Window
        Return: window_dto: WindowDto
        '''

        window_id = self.window_id
        center_point_dto = self.center_point.convert_to_dto()
        start_point_dto = self.start_point.convert_to_dto()
        end_point_dto = self.end_point.convert_to_dto()
        radius = self.radius
        angle = self.angle
        is_matched = self.is_matched
        amount_matched = self.amount_matched
        return WindowDto(center_point_dto, start_point_dto, end_point_dto, radius, angle, window_id=window_id, amount_matched=amount_matched, is_matched=is_matched)
