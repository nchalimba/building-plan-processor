
from datetime import datetime

from app.main.constants import (PLOT_SAVE_DIRECTORY, TIME_STAMP_FORMAT,
                                PlotStyle)
from app.main.models.wall import Wall
from matplotlib import pyplot as plt

'''
Description: This method contains helper functions for plotting and reporting.
'''

class ReportingHelper:
    @staticmethod
    def get_file_path(plot_type: str) -> str:
        '''
        Description: This method creates a file path for a plot with a given plot type.
        Params: plot_type: str
        Return: file_path: str
        '''
        now = datetime.now()
        date_time = now.strftime(TIME_STAMP_FORMAT)

        return PLOT_SAVE_DIRECTORY + date_time + plot_type + ".png"

    @staticmethod
    def legend_without_duplicate_labels(ax) -> list[tuple]:
        '''
        Description: This method is used to get unique values for plot_legend
        Params: ax: Axes
        Return: unique: list[tuple]
        Exception: None
        '''
        handles, labels = ax.get_legend_handles_labels()
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
        return unique
    
    @staticmethod
    def plot_room_number_on_wall(wall: Wall, room_number) -> tuple[str, (float, float), (float, float), int, dict, dict]:
        '''
        Description: This method is used to plot room label on a wall
        Params: wall: Wall, room_number: str
        Return: message: str, xy: (float, float), xytext: (float, float), size: int, bbox: dict, arrowprops: dict
        Exception: None
        '''
        wall_x_coordinate = wall.start_point.x_coordinate
        wall_y_coordinate = wall.end_point.y_coordinate
        message = ("{}".format(room_number))
        size = PlotStyle.ROOM_LABEL_SIZE.value
        bbox = dict(boxstyle="round", fc="w", lw=0.25, alpha=0.75)
        arrowprops=dict(arrowstyle="-|>",connectionstyle="arc3", facecolor="black", lw=0.25)
        return message, (wall_x_coordinate, wall_y_coordinate), (wall_x_coordinate, wall_y_coordinate - PlotStyle.ROOM_LABEL_Y_POS.value), size, bbox, arrowprops

