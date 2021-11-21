from app.main.constants import PLOT_DPI, PLOT_LINE_WIDTH_NORMAL, PlotTypes, DefaultColors, PlotStyle
from app.main.models.polygon import Polygon
from app.main.reporting.reporting_helper import ReportingHelper
from app.main.services.extraction_helper import ExtractionHelper
from matplotlib import pyplot as plt

'''
Description: This class plots unmatched room annotations
'''

class UnmatchedRoomPlotter:

    def plot_unmatched_roomstamps(self, polygons: list[Polygon], unmatched_rooms: list[Polygon], coordinates: list = None) -> str:
        '''
        Description: This method plots unmatched room annotations of an simple plan.
        Params: polygons: list[Polygon], unmatched_rooms: list[Polygon]
        Return: file_path: str
        '''
        
        for polygon in polygons:
            walls = polygon.walls
            for wall in walls:
                plt.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                    wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.GRAY.value, linewidth=PLOT_LINE_WIDTH_NORMAL)
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

        for unmatched_room in unmatched_rooms:
            label           = unmatched_room[0][1]
            x_coordinate    = unmatched_room[0][2]
            y_coordinate    = unmatched_room[0][3]
            plt.annotate(label,
                    xy=(x_coordinate, y_coordinate),
                    xytext=(x_coordinate, y_coordinate - 20),
                    size=6, bbox=dict(boxstyle="round", fc="w", lw=0.25, alpha=0.75),
                    arrowprops=dict(arrowstyle="-|>",connectionstyle="arc3", facecolor="black", lw= 0.25))

        file_path = ReportingHelper.get_file_path(PlotTypes.UNMATCHED_ROOM_PLOT.value)
        plt.tick_params(axis=PlotStyle.AXIS.value, left=PlotStyle.TICKS_LEFT.value, bottom=PlotStyle.TICKS_BOTTOM.value, labelleft=PlotStyle.LABEL_LEFT.value, labelbottom=PlotStyle.LABEL_BOTTOM.value)
        plt.savefig(file_path, dpi=PLOT_DPI, transparent=PlotStyle.TRANSPARENT)
        plt.clf()
        return file_path 
   