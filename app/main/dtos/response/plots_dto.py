from dataclasses import dataclass, field

from app.main.dtos.response.general_plot_dto import GeneralPlotDto
from app.main.dtos.response.polygon_plot_dto import PolygonPlotDto


@dataclass
class PlotsDto:
    general_plots: list[GeneralPlotDto]
    polygon_plots: list[PolygonPlotDto] = field(default=None)
