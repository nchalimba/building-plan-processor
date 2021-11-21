import matplotlib
from app.main.constants import (PLOT_DPI, PLOT_LINE_WIDTH_LARGE,
                                PLOT_LINE_WIDTH_SMALL, DefaultColors,
                                OrientationColors, PlotStyle, PlotTypes)
from app.main.models.polygon import Polygon
from app.main.reporting.reporting_helper import ReportingHelper

matplotlib.use('Agg')
from matplotlib import pyplot as plt

'''
Description: This class contains the logic to plot the walls of polygons and to draw outer walls in red.
'''

class WallPlotter:

    def plot_walls(self, polygons: list[Polygon], coordinates: list[tuple] = None, is_orientation: bool = False) -> str:
        '''
        Description: This class plots walls of polygons from a simple plan and highlights outer walls.
        Params: polygons: list, coordinates: list, is_orientation: bool
        Return: file_path: str
        '''
        fig, ax = plt.subplots()
        orientation_found = False
        for polygon in polygons:
            walls = polygon.walls
            for wall in walls:
        
                if(wall.is_outer_wall and not is_orientation):
                    ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                        wall.start_point.y_coordinate, wall.end_point.y_coordinate], color=DefaultColors.RED.value, linewidth=PLOT_LINE_WIDTH_LARGE)
                elif(wall.sky_direction and is_orientation):
       
                    if(wall.sky_direction == OrientationColors.NORTH.name.lower()):
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate],
                            color=OrientationColors.NORTH.value, label=OrientationColors.NORTH.name.lower(), linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif(wall.sky_direction == OrientationColors.NORTH_EAST.name.lower()):
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate],
                            color=OrientationColors.NORTH_EAST.value, label=OrientationColors.NORTH_EAST.name.lower(), linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif(wall.sky_direction == OrientationColors.EAST.name.lower()):
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate],
                            color=OrientationColors.EAST.value, label=OrientationColors.EAST.name.lower(), linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif(wall.sky_direction == OrientationColors.SOUTH_EAST.name.lower()):
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate],
                            color=OrientationColors.SOUTH_EAST.value, label=OrientationColors.SOUTH_EAST.name.lower(), linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif(wall.sky_direction == OrientationColors.SOUTH.name.lower()):
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate],
                            color=OrientationColors.SOUTH.value, label=OrientationColors.SOUTH.name.lower(), linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif(wall.sky_direction == OrientationColors.SOUTH_WEST.name.lower()):
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate],
                            color=OrientationColors.SOUTH_WEST.value, label=OrientationColors.SOUTH_WEST.name.lower(), linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif(wall.sky_direction == OrientationColors.WEST.name.lower()):
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate],
                            color=OrientationColors.WEST.value, label=OrientationColors.WEST.name.lower(), linewidth=PLOT_LINE_WIDTH_LARGE)
                    elif(wall.sky_direction == OrientationColors.NORTH_WEST.name.lower()):
                        ax.plot([wall.start_point.x_coordinate, wall.end_point.x_coordinate], [
                            wall.start_point.y_coordinate, wall.end_point.y_coordinate],
                            color=OrientationColors.NORTH_WEST.value, label=OrientationColors.NORTH_WEST.name.lower(), linewidth=PLOT_LINE_WIDTH_LARGE)
                    orientation_found = True
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
        if is_orientation and not orientation_found:
            return "ERROR"
        if is_orientation:
            ax.legend(loc="upper right")
            unique_legendes = ReportingHelper.legend_without_duplicate_labels(ax)
            ax.legend(*zip(*unique_legendes))
        file_path = ReportingHelper.get_file_path(PlotTypes.WALL_PLOT.value)
        plt.tick_params(axis=PlotStyle.AXIS.value, left=PlotStyle.TICKS_LEFT.value, bottom=PlotStyle.TICKS_BOTTOM.value, labelleft=PlotStyle.LABEL_LEFT.value, labelbottom=PlotStyle.LABEL_BOTTOM.value)
        plt.savefig(file_path, dpi=PLOT_DPI, transparent=PlotStyle.TRANSPARENT)
        plt.clf()
        return file_path
