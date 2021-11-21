from enum import Enum
from math import e

import matplotlib
from app.main.constants import (MATCHED_WALL_TYPES, PLOT_DPI,
                                PLOT_LINE_WIDTH_LARGE, PLOT_LINE_WIDTH_NORMAL,
                                PLOT_LINE_WIDTH_SMALL, DefaultColors,
                                NeighbourColors, PlotStyle, PlotTypes)
from app.main.models.architecture_plan import Architecture_Plan
from app.main.models.polygon import Polygon
from app.main.models.simple_plan import Simple_Plan
from app.main.reporting.reporting_helper import ReportingHelper
from matplotlib import pyplot as plt

matplotlib.use('Agg')
'''
Description: This class plots plots windows and pillars of an matched architecture plan
'''

class WindowPillarPlotter:

    def plot_window_and_pillar(self, polygons: list[Polygon], architecture_plan: Architecture_Plan = None, coordinates: list = None) -> str:
        '''
        Description: This method plots windows and pillars of an architecture plan matched into a simple plan as well pillars of an architecture Plan.
        Params: polygons: list[Polygon], architecture_plan: Architecture_Plan
        Return: file_path: str
        '''
        if polygons:
            fig, ax = plt.subplots()
            for polygon in polygons:
                walls = polygon.walls
                for wall in walls:
                    ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.GRAY.value, linewidth=PLOT_LINE_WIDTH_SMALL)
                try:
                    for window in polygon.windows:
                        if window.is_matched:
                            ax.plot([window.start_point.x_coordinate, window.end_point.x_coordinate], [window.start_point.y_coordinate, window.end_point.y_coordinate], color=DefaultColors.GREEN.value, label="matched windows", linewidth=PLOT_LINE_WIDTH_LARGE)
                except Exception:
                    pass

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
                    
        for pillar in architecture_plan.pillars:
            if pillar.is_matched:
                pillar_color = DefaultColors.PINK.value
                label = "matched pillars"
            else:
                pillar_color = DefaultColors.CYAN.value
                label = "unmatched pillars"
            if pillar.points:
                points_x = [point.x_coordinate for point in pillar.points]
                points_y = [point.y_coordinate for point in pillar.points]
                ax.fill(points_x, points_y, color=pillar_color, label=label)
            elif pillar.center_point:
                circle = plt.Circle((pillar.center_point.x_coordinate, pillar.center_point.y_coordinate), pillar.radius, color=pillar_color, label=label, fill=True)
                ax.add_patch(circle)

        file_path = ReportingHelper.get_file_path(PlotTypes.ARCHITECTURE_PILLARS_AND_WINDOWS_PLOT.value)
        ax.legend(loc="upper right")
        unique_legendes = ReportingHelper.legend_without_duplicate_labels(ax)
        ax.legend(*zip(*unique_legendes))
        plt.tick_params(axis=PlotStyle.AXIS.value, left=PlotStyle.TICKS_LEFT.value, bottom=PlotStyle.TICKS_BOTTOM.value, labelleft=PlotStyle.LABEL_LEFT.value, labelbottom=PlotStyle.LABEL_BOTTOM.value)
        plt.savefig(file_path, dpi=PLOT_DPI, transparent=PlotStyle.TRANSPARENT)
        plt.clf()
        return file_path
