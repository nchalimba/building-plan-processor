from app.main.models.polygon import Polygon
from app.main.constants import (PLOT_DPI, PLOT_LINE_WIDTH_LARGE, DefaultColors,
                                NeighbourColors, PlotStyle, PlotTypes)
from app.main.reporting.reporting_helper import ReportingHelper
from matplotlib import pyplot as plt

'''
Description: This class plots the neighbour rooms
'''

class AdjacentPlotter:

    def plot_adjacent_polygons(self, polygons: list[Polygon], coordinates: list = None) -> str:
        '''
        Description: This method plots neighbour rooms of an simple plan.
        Params: polygons: list[Polygon]
        Return: file_path: str
        '''
        fig, ax = plt.subplots()

        for polygon in polygons:
            count_potential_neighbours = 0
            walls = polygon.walls
            try:
                count_potential_neighbours = len(polygon.adjacent_polygons)
            except Exception:
                pass
            
            for wall in walls:
                if count_potential_neighbours:
                    if 0 < count_potential_neighbours < 2:
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                                    wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=NeighbourColors.LESS_THAN_TWO.value, label="< 2 Neighbours", linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif 2 <= count_potential_neighbours < 4:
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                                    wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=NeighbourColors.LESS_THAN_FOUR.value, label="< 4 Neighbours", linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif 4 <= count_potential_neighbours < 6:
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                                    wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=NeighbourColors.LESS_THAN_SIX.value, label="< 6 Neighbours" , linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif 6 <= count_potential_neighbours < 8:
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                                    wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=NeighbourColors.LESS_THAN_EIGHT.value, label="< 8 Neighbours", linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif count_potential_neighbours >= 8:
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                                    wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=NeighbourColors.MORE_THAN_EIGHT.value, label=">= 8 Neighbours", linewidth=PLOT_LINE_WIDTH_LARGE)        
                else:
                    ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                                    wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=NeighbourColors.LESS_THAN_ONE.value, label="0 Neighbours", linewidth=PLOT_LINE_WIDTH_LARGE)
            if coordinates != None:
                coordinates_x = [coordinate[0] for coordinate in coordinates]
                coordinates_y = [coordinate[1] for coordinate in coordinates]
                ax.plot(coordinates_x, coordinates_y, 'bo')

                i = 0
                for x, y in zip(coordinates_x, coordinates_y):
                    label = str(i)
                    ax.annotate(label,
                                 (x, y),
                                 textcoords="offset points",
                                 xytext=(0, 10),
                                 ha='center')
                    i = i + 1
        
        ax.legend(loc="upper right")
        unique_legendes = ReportingHelper.legend_without_duplicate_labels(ax)
        ax.legend(*zip(*unique_legendes))
        file_path = ReportingHelper.get_file_path(PlotTypes.ADJACENT_PLOT.value)
        plt.tick_params(axis=PlotStyle.AXIS.value, left=PlotStyle.TICKS_LEFT.value, bottom=PlotStyle.TICKS_BOTTOM.value, labelleft=PlotStyle.LABEL_LEFT.value, labelbottom=PlotStyle.LABEL_BOTTOM.value)
        plt.savefig(file_path, dpi=PLOT_DPI, transparent=PlotStyle.TRANSPARENT)
        plt.clf()
        return file_path