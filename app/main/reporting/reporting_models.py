from dataclasses import dataclass, field
from datetime import datetime

from app.main.constants import PlotTypes
from app.main.dtos.response.general_plot_dto import GeneralPlotDto
from app.main.dtos.response.plots_dto import PlotsDto
from app.main.dtos.response.report_dto import ReportDto

'''
Description: This file contains classes that represent the payload necessary for creating a report.
'''

'''
Description: This class represents information about which data could be extracted.
'''
@dataclass
class ExtractedFunctionalities:
    outer_walls: bool = field(default=False)
    match_room: bool = field(default=False)
    area: bool = field(default=False)
    perimeter: bool = field(default=False)
    orientation: bool = field(default=False)
    neighbours: bool = field(default=False)
    architecture_light_walls: bool = field(default=False)
    architecture_load_bearing_walls: bool = field(default=False)
    architecture_pillars: bool = field(default=False)
    architecture_windows: bool = field(default=False)
    architecture_facade_arcs: bool = field(default=False)
    architecture_facade_lines: bool = field(default=False)


'''
Description: This class contains the structure of log messages within the report.
'''
@dataclass
class LogMessage:
    scope: str
    topic: str
    message: str
    time_stamp: str = field(default=None)

    def __repr__(self) -> str:
        '''
        Description: This method defines how a log message is converted to a string.
        Params: self: LogMessage
        Return: repr: str
        '''
        return '[{0}] {1}: {2}'.format(self.scope, self.topic, self.message)


'''
Description: This class contains the structure of the metadata of plots.
'''
@dataclass
class Plot:
    plot_path: str
    plot_title: str
    plot_caption: str
    polygon_id: str = field(default=None)

    def convert_to_general_dto(self, category: str)-> GeneralPlotDto:
        return GeneralPlotDto(category, self.plot_title, self.plot_path)


'''
Description: This class contains the structure of a row in the area table of the report.
'''
@dataclass
class AreaTableRow:
    room_number: str
    area_calculated: float
    area_annotation: float
    area_deviation: float

'''
Description: This class contains the structure of a row in the perimeter table of the report.
'''
@dataclass
class PerimeterTableRow:
    room_number: str
    perimeter_calculated: float
    perimeter_actual: float
    perimeter_deviation: float


'''
Description: This class contains the structure of the key data about the area.
'''
@dataclass
class AreaData:
    amount_rooms: int
    acceptable_deviation: int
    amount_miscalculated_rooms: int
    failure_rate: int
    area_table_rows: list[AreaTableRow]

'''
Description: This class contains the structure of the key data about the perimeter.
'''
@dataclass
class PerimeterData:
    amount_rooms: int
    perimeter_table_rows: list[PerimeterTableRow]

'''
Description: This class contains the structure of the key data about the area.
'''
@dataclass
class ReportingPayload:
    extracted_functionalities: ExtractedFunctionalities
    unmatched_rooms: list[str]
    area_data: AreaData
    perimeter_data: PerimeterData
    log_messages: list[LogMessage]
    outer_wall_plot: Plot= field(default=None)
    unmatched_room_plot: Plot= field(default=None)
    area_plot: Plot= field(default=None)
    perimeter_plot: Plot= field(default=None)
    orientation_plot: Plot= field(default=None)
    neighbour_plot: Plot = field(default=None)
    architecture_walls_plot: Plot = field(default=None)
    architecture_pillars_and_windows_plot: Plot = field(default=None)
    architecture_facade_plot: Plot = field(default=None)
    plan_file_path: str = field(default=None)
    plan_file_name: str = field(default=None)

    def convert_to_dto(self, filepath) -> ReportDto:
        '''
        Description: This method converts a reporting payload instance into the api representation.
        Params: self: ReportingPayload, filepath: str
        Return: ReportDto
        '''
        general_plots = []
        if self.outer_wall_plot:
            general_plots.append(self.outer_wall_plot.convert_to_general_dto(PlotTypes.OUTER_WALL_PLOT.value))
        if self.unmatched_room_plot:
            general_plots.append(self.unmatched_room_plot.convert_to_general_dto(PlotTypes.UNMATCHED_ROOM_PLOT.value))
        if self.area_plot:
            general_plots.append(self.area_plot.convert_to_general_dto(PlotTypes.AREA_PLOT.value))
        if self.perimeter_plot:
            general_plots.append(self.perimeter_plot.convert_to_general_dto(PlotTypes.PERIMETER_PLOT.value))
        if self.orientation_plot:
            general_plots.append(self.orientation_plot.convert_to_general_dto(PlotTypes.OUTER_WALL_ORIENTATION_PLOT.value))
        if self.neighbour_plot:
            general_plots.append(self.neighbour_plot.convert_to_general_dto(PlotTypes.ADJACENT_PLOT.value))
        if self.architecture_walls_plot:
            general_plots.append(self.architecture_walls_plot.convert_to_general_dto(PlotTypes.ARCHITECTURE_WALLS_PLOT.value))
        if self.architecture_pillars_and_windows_plot:
            general_plots.append(self.architecture_pillars_and_windows_plot.convert_to_general_dto(PlotTypes.ARCHITECTURE_PILLARS_AND_WINDOWS_PLOT.value))
        if self. architecture_facade_plot:
            general_plots.append(self.architecture_facade_plot.convert_to_general_dto(PlotTypes.ARCHITECTURE_FACADE_PLOT.value))
        plots = PlotsDto(general_plots)
        return ReportDto(filepath, plots)
        
