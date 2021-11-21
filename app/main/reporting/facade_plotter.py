
from app.main.constants import (MATCHED_WALL_TYPES, PLOT_DPI,
                                PLOT_LINE_WIDTH_LARGE, PLOT_LINE_WIDTH_NORMAL,
                                PLOT_LINE_WIDTH_SMALL, DefaultColors,
                                NeighbourColors, PlotStyle, PlotTypes)
from app.main.models.architecture_plan import Architecture_Plan
from app.main.models.polygon import Polygon
from app.main.reporting.reporting_helper import ReportingHelper
from matplotlib import pyplot as plt

'''
Description: This class plots the facade lines and arcs
'''
class FacadePlotter:
    def plot_facade(self, architecture_plan: Architecture_Plan, polygons: list[Polygon] = None) -> str:
        '''
        Description: This method plots facade lines and facade arcs of an architecture plan as well as polygons of a simple plan.
        Params: architecture_plan: Architecture_Plan, polygons: list[Polygon]
        Return: file_path: str
        '''

        fig, ax = plt.subplots()
        if polygons:
            for polygon in polygons:
                walls = polygon.walls
                for wall in walls:
                    ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.GRAY.value, linewidth=PLOT_LINE_WIDTH_SMALL)
        

        for facade_arc in architecture_plan.facade_arcs:
            if not facade_arc.lines:
                continue
            for line in facade_arc.lines:
                ax.plot([line.start_point.x_coordinate, line.end_point.x_coordinate], [line.start_point.y_coordinate, line.end_point.y_coordinate], color=DefaultColors.CYAN.value, label="facade arcs", linewidth=PLOT_LINE_WIDTH_NORMAL)
        for facade_line in architecture_plan.facade_lines:
            ax.plot([facade_line.start_point.x_coordinate, facade_line.end_point.x_coordinate], [facade_line.start_point.y_coordinate, facade_line.end_point.y_coordinate], color=DefaultColors.PINK.value, label="facade lines", linewidth=PLOT_LINE_WIDTH_NORMAL)
        
        file_path = ReportingHelper.get_file_path(PlotTypes.ARCHITECTURE_FACADE_PLOT.value)
        ax.legend(loc="upper right")
        unique_legendes = ReportingHelper.legend_without_duplicate_labels(ax)
        ax.legend(*zip(*unique_legendes))
        plt.tick_params(axis=PlotStyle.AXIS.value, left=PlotStyle.TICKS_LEFT.value, bottom=PlotStyle.TICKS_BOTTOM.value, labelleft=PlotStyle.LABEL_LEFT.value, labelbottom=PlotStyle.LABEL_BOTTOM.value)
        plt.savefig(file_path, dpi=PLOT_DPI, transparent=PlotStyle.TRANSPARENT)
        plt.clf()
        return file_path