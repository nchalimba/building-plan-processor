from app.main.reporting.reporting_models import AreaData, PerimeterData
from app.main.constants import PLOT_DPI, PLOT_LINE_WIDTH_LARGE, PLOT_LINE_WIDTH_SMALL, PlotTypes, DefaultColors, PlotStyle
from app.main.reporting.reporting_helper import ReportingHelper
from matplotlib import pyplot as plt
from app.main.models.polygon import Polygon

'''
Description: This class plots perimeter_calculated != perimeter_validation
'''

class PerimeterPlotter:

    def plot_miscalculated_perimeter(self, polygons: list[Polygon], perimeter_data: PerimeterData, coordinates: list = None) -> str:
        '''
        Description: This method plots perimeter_calculated of rooms. If perimeter_calculated != perimeter_validation: red; otherwise green. 
            using perimeter_validation data stored in app.test.test_data.perimeter_validation.py
        Params: polygons: list[Polygon], perimeter_data: PerimeterData
        Return: file_path: str
        '''
        for polygon in polygons:
            perimeter_checked_room = False
            table_row_area_deviation = 0.00
            try:
                room_number = polygon.room.room_number
                for table_row in perimeter_data.perimeter_table_rows:
                    table_row_room_number = table_row.room_number
                    if room_number == table_row_room_number:
                        perimeter_checked_room = True
                        table_row_area_deviation = table_row.perimeter_deviation
                        break
            except (KeyError, AttributeError):
                pass

            walls = polygon.walls
            count_walls = 0
            for wall in walls:
                count_walls += 1
                if perimeter_checked_room:
                    if table_row_area_deviation > 5:
                        plt.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.RED.value, linewidth=PLOT_LINE_WIDTH_LARGE)
                    else:
                        plt.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.GREEN.value, linewidth=PLOT_LINE_WIDTH_LARGE)
                    if count_walls == len(walls):
                        message, xy, xytext, size, bbox, arrowprops = ReportingHelper.plot_room_number_on_wall(wall, room_number)
                        plt.annotate(text=message, xy=xy, xytext=xytext, size=size, bbox=bbox, arrowprops=arrowprops)
                else:
                     plt.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                        wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.GRAY.value, linewidth=PLOT_LINE_WIDTH_SMALL)
            
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
        file_path = ReportingHelper.get_file_path(PlotTypes.PERIMETER_PLOT.value)
        plt.tick_params(axis=PlotStyle.AXIS.value, left=PlotStyle.TICKS_LEFT.value, bottom=PlotStyle.TICKS_BOTTOM.value, labelleft=PlotStyle.LABEL_LEFT.value, labelbottom=PlotStyle.LABEL_BOTTOM.value)
        plt.savefig(file_path, dpi=PLOT_DPI, transparent=PlotStyle.TRANSPARENT)
        plt.clf()
        return file_path