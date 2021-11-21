from app.main.models.wall import Wall
from app.main.reporting.reporting_models import AreaData
from app.main.constants import PLOT_DPI, PLOT_LINE_WIDTH_NORMAL, PLOT_LINE_WIDTH_LARGE, PlotTypes, DefaultColors, PlotStyle

from app.main.reporting.reporting_helper import ReportingHelper
from app.main.services.extraction_helper import ExtractionHelper
from matplotlib import pyplot as plt
from app.main.models.polygon import Polygon

'''
Description: This class plots area_calculated != area_annotation
'''

class AreaPlotter:

    def plot_miscalculated_room_area(self, polygons: list[Polygon], area_data: AreaData, coordinates: list = None) -> str:
        '''
        Description: This method plots area calculated of rooms. If area_calculated != area_annotation: red; otherwise green
        Params: polygons: list[Polygon], area_data: AreaData
        Return: file_path: str
        '''
        for polygon in polygons:
            miscalculated_room = False
            try:
                room_number = polygon.room.room_number
                for table_row in area_data.area_table_rows:
                    table_row_room_number = table_row.room_number
                    if room_number == table_row_room_number:
                        miscalculated_room = True
                        continue
            except (KeyError, AttributeError):
                pass
            
            walls = polygon.walls
            count_walls = 0
            for wall in walls:
                count_walls += 1 
                if miscalculated_room:
                    plt.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                        wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.RED.value, linewidth=PLOT_LINE_WIDTH_LARGE)
                    if count_walls == len(walls):
                        message, xy, xytext, size, bbox, arrowprops = ReportingHelper.plot_room_number_on_wall(wall, room_number)
                        plt.annotate(text=message, xy=xy, xytext=xytext, size=size, bbox=bbox, arrowprops=arrowprops)
                else:
                     plt.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                        wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.GREEN.value, linewidth=PLOT_LINE_WIDTH_NORMAL)

            if coordinates != None:
                coordinates_x = [coordinate[0] for coordinate in coordinates]
                coordinates_y = [coordinate[1] for coordinate in coordinates]
                plt.plot(coordinates_x, coordinates_y, 'bo')

                i = 0
                for x, y in zip(coordinates_x, coordinates_y):
                    label = str(i)
                    plt.annotate(label,
                                 (x, y),
                                 textcoords="offset points",
                                 xytext=(0, 10),
                                 ha='center')
                    i = i + 1
        file_path = ReportingHelper.get_file_path(PlotTypes.AREA_PLOT.value)
        plt.tick_params(axis=PlotStyle.AXIS.value, left=PlotStyle.TICKS_LEFT.value, bottom=PlotStyle.TICKS_BOTTOM.value, labelleft=PlotStyle.LABEL_LEFT.value, labelbottom=PlotStyle.LABEL_BOTTOM.value)
        plt.savefig(file_path, dpi=PLOT_DPI, transparent=PlotStyle.TRANSPARENT)
        plt.clf()
        return file_path