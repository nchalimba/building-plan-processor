from enum import Enum

import matplotlib
from app.main.constants import (MATCHED_WALL_TYPES, PLOT_DPI,
                                PLOT_LINE_WIDTH_LARGE, PLOT_LINE_WIDTH_NORMAL,
                                PLOT_LINE_WIDTH_SMALL, PLOT_LINE_WIDTH_HUGE, DefaultColors, MatchedWallStyle,
                                NeighbourColors, PlotStyle, PlotTypes)
from app.main.reporting.reporting_helper import ReportingHelper
from app.main.models.polygon import Polygon
from matplotlib import pyplot as plt

matplotlib.use('Agg')
'''
Description: This class plots matched walls
'''
class MatchedWallsPlotter:

    def plot_walls(self, polygons: list[Polygon], coordinates: list = None) -> str:
        '''
        Description: This method plots walls of an architecture matched into a simple plan.
        Params: polygons: list[Polygon]
        Return: file_path: str
        '''
        fig, ax = plt.subplots()
        wall_type_found = False
        for polygon in polygons:
            walls = polygon.walls
            for wall in walls:
                if (wall.wall_type == MATCHED_WALL_TYPES.LOAD_BEARING_WALL.name.lower()):
                    linestyle, plot_label, linewidth = self.get_linestyle_label_and_linewidth(wall)
                    ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                        wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.GREEN.value, label=MATCHED_WALL_TYPES.LOAD_BEARING_WALL.value + plot_label, ls=linestyle, linewidth=linewidth)
                    wall_type_found = True
                
                elif (wall.wall_type == MATCHED_WALL_TYPES.LIGHT_WALL.name.lower()):
                    linestyle, plot_label, linewidth = self.get_linestyle_label_and_linewidth(wall)
                    ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                        wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.RED.value, label=MATCHED_WALL_TYPES.LIGHT_WALL.value + plot_label, ls=linestyle, linewidth=linewidth)
                    wall_type_found = True

                else:
                    ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.GRAY.value, linewidth=PLOT_LINE_WIDTH_SMALL)
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
        file_path = ReportingHelper.get_file_path(PlotTypes.ARCHITECTURE_WALLS_PLOT.value)
        if wall_type_found:
            unique_legendes = ReportingHelper.legend_without_duplicate_labels(ax)
            ax.legend(*zip(*unique_legendes))
        plt.tick_params(axis=PlotStyle.AXIS.value, left=PlotStyle.TICKS_LEFT.value, bottom=PlotStyle.TICKS_BOTTOM.value, labelleft=PlotStyle.LABEL_LEFT.value, labelbottom=PlotStyle.LABEL_BOTTOM.value)
        plt.savefig(file_path, dpi=PLOT_DPI, transparent=PlotStyle.TRANSPARENT)
        plt.clf()
        return file_path

    def get_linestyle_label_and_linewidth(self, wall) -> tuple[str, str, float]:
        '''
        Description: This method is used to get MatchedWallStyle for a wall. Defined in constants.py
        Params: wall: Wall
        Return: MatchedWallStyle.LINESTYLE*.value: str, MatchedWallStyle.*RANGE.value: str, PLOT_LINE_WIDTH: float
        '''
        if 0 < wall.wall_thickness < 0.15:
            return MatchedWallStyle.LINESTYLE_SOLID.value, MatchedWallStyle.SOLID_RANGE.value, PLOT_LINE_WIDTH_SMALL
        elif 0.15 < wall.wall_thickness < 0.20:
            return MatchedWallStyle.LINESTYLE_DOTTED.value, MatchedWallStyle.DOTTED_RANGE.value, PLOT_LINE_WIDTH_NORMAL
        elif 0.20 < wall.wall_thickness < 0.25:
            return MatchedWallStyle.LINESTYLE_DASHED.value, MatchedWallStyle.DASHED_RANGE.value, PLOT_LINE_WIDTH_LARGE
        elif 0.25 < wall.wall_thickness < 0.35:
            return MatchedWallStyle.LINESTYLE_DASHDOT.value, MatchedWallStyle.DASHDOT_RANGE.value, PLOT_LINE_WIDTH_HUGE
        else:
            return None, MatchedWallStyle.UNKNOWN_RANGE.value, PLOT_LINE_WIDTH_SMALL