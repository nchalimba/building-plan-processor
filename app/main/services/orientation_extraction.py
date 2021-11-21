import math

import ezdxf
import shapely.geometry as geom
from app.main.constants import *
from app.main.models.wall import Wall
from app.main.services.extraction_helper import ExtractionHelper
from loguru import logger
from numpy import arctan2, array, dot

'''
Description: This service provides functionalities for the determination of the orientation in simple plans. 
'''

main_logger = logger.bind()


class OrientationExtraction:

    @staticmethod
    def center_of_line(x_1: float, x_2: float, y_1: float, y_2: float) -> tuple:
        '''
        Description: This method uses 'centerOfLine()' method. Calculates the center of a line and is used in get_north_orientation().
        Params: x_1: float, x_2: float, y_1: float, y_2: float
        Return: tuple of x_coordinate: float, y_coordinate: float
        '''

        x_coordinate = x_1 - 0.5 * (x_1 - x_2)
        y_coordinate = y_1 - 0.5 * (y_1 - y_2)
        return tuple((x_coordinate, y_coordinate))

    @staticmethod
    def get_north_orientation(file_path: str) -> tuple[tuple, array, array]:
        '''
        Description: Builds upon the 'getNorthOrientation()' method . This method extracts the compass embedded in simple plans and creates a north oriented coordinate system.
        Params: file_path: str
        Return: origin: tuple[float], xaxis: ndarray, yaxis: ndarray
        '''

        # read dxf file
        dxf_compass_EG = ezdxf.readfile(file_path)

        # getting paperspace layout by name (bestandplan-compass)
        psp = dxf_compass_EG.layout(NUDATA_COMPASS_LAYOUT)

        # extract the entire compass (all lines of layer 0)
        polylines = [p for p in psp.query('LWPolyline [layer == "0"]')]

        # extract lines of compass
        if len(polylines) == 2:
            listOfPoints = []
            for line in polylines:
                listOfPoints.append((line.get_points()))

            if listOfPoints[0][0] == listOfPoints[1][0]:
                yaxis_endpoint = tuple(
                    (listOfPoints[0][0][0], listOfPoints[0][0][1]))
                yaxis_startpoint = []

                x1 = listOfPoints[0][1][0]
                x2 = listOfPoints[1][1][0]
                y1 = listOfPoints[0][1][1]
                y2 = listOfPoints[1][1][1]

                # possilbe rotations of the compass
                if x1 > x2 and y1 > y2:
                    yaxis_startpoint = OrientationExtraction.center_of_line(
                        x1, x2, y1, y2)
                elif x1 > x2 and y2 > y1:
                    yaxis_startpoint = OrientationExtraction.center_of_line(
                        x1, x2, y2, y1)
                elif x2 > x1 and y1 > y2:
                    yaxis_startpoint = OrientationExtraction.center_of_line(
                        x2, x1, y1, y2)
                elif x2 > x1 and y2 > y1:
                    yaxis_startpoint = OrientationExtraction.center_of_line(
                        x2, x1, y2, y1)

                yaxis_x = yaxis_endpoint[0] - yaxis_startpoint[0]
                yaxis_y = yaxis_endpoint[1] - yaxis_startpoint[1]

                origin = yaxis_startpoint
                xaxis = array([-yaxis_x, yaxis_y, 0.0])
                yaxis = array([-yaxis_y, -yaxis_x, 0.0])

                main_logger.success(
                    "Compass extraction successful, return coordinate system")

                return origin, xaxis, yaxis

    @staticmethod
    def get_north_orientation_by_angle(angle = None) -> array:
        '''
        Description: This method determines north orientation by a given angle. Generates yaxis which points north.
        Params: angle
        Return: yaxis: ndarray
        '''

        if angle is None:
            yaxis = array([0, 1, 0])
            main_logger.info('Default Orientation, north is central top')
            return yaxis
        else:
            angle_transformed = 360.0 - angle
            alpha = math.radians(angle_transformed)
            perpendicular_line = array([0, 1, 0])

            # Rotation axis (z-axis)
            axis = array([0, 0, 1])
            yaxis = array(dot(OrientationExtraction.generate_rotation_matrix(
                axis, alpha), perpendicular_line))
            main_logger.info('Orientation angle successfully determined, return yaxis')
            return yaxis

    @staticmethod
    def generate_rotation_matrix(axis: float, alpha: float) ->  array:
        """
        Description: This Method uses Euler-Rodrigues formular to generate rotation matrix (rotation about the axis by alpha in radians). Used in get_north_orientation_by_angle().
        Params: axis: float, alpha:float
        Returns: array
        """

        axis = axis / math.sqrt(dot(axis, axis))
        a = math.cos(alpha / 2.0)
        b, c, d = -axis * math.sin(alpha / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                      [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                      [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    @staticmethod
    def calculate_orientation(direction, yaxis, wall: Wall):
        '''
        Method to calculate the orientation of a wall referring to the north-heading coordinate system. The methode
        builds a wall line and a parallel line with offset 1. A perpendicular line between wall line and parallel line
        is generated. The method uses the perpendicular line to calculate the angle between wall and north coordinate system.
        Returns a angle in degrees.

        :param yaxis: vector of the coordinate system (array[float])
        :param direction:String (left or right)
        :return angle: float
        '''
        this_wall_line = ExtractionHelper.transform_wall_to_line_string(wall)
        this_wall_line_middle = geom.Point((wall.start_point.x_coordinate + wall.end_point.x_coordinate) / 2,
                                           (wall.start_point.y_coordinate + wall.end_point.y_coordinate) / 2)

        # build parallel line
        parallel_line = this_wall_line.parallel_offset(1, direction)
        parallel_line_middle = geom.Point(
            (parallel_line.coords[0][0] + parallel_line.coords[1][0]) / 2,
            (parallel_line.coords[0][1] + parallel_line.coords[1][1]) / 2)

        # build perpendicular line
        x_1 = float(this_wall_line_middle.x)
        x_2 = float(parallel_line_middle.x)
        y_1 = float(this_wall_line_middle.y)
        y_2 = float(parallel_line_middle.y)

        perpendicular_line = array([0, 0, 0], dtype=float)

        perpendicular_line[0] = x_2-x_1
        perpendicular_line[1] = y_2-y_1

        # calculate angle
        angle = OrientationExtraction.full_angle_between(
            perpendicular_line, yaxis)

        return angle

    @staticmethod
    def full_angle_between(v1, v2):
        '''
        Method to calculate the angle between perpendicular_line of wall and north-orientated coordinate system.
        The method returns angle in range of 0-360 degrees. Orientation is clockwise turning. -->
        0 = north, 90 = east, 180 = south, 270 = west

        .:param v1 -> perpendicular line to wall, v2 -> yaxis of north-coordinate system
        :return angle in degrees: float
        '''
        dot = v1[0]*v2[0]+v1[1]*v2[1]
        det = v1[0]*v2[1]-v2[0]*v1[1]

        angle = math.degrees(arctan2(det, dot))
        if angle < 0:
            angle = 360-abs(angle)

        return angle

    @staticmethod
    def sky_direction(angle: float):
        '''
        Description: This method determines the sky direction for a given angle (0-360) in degree.
        Params: angle: float
        Return: direction: Literal
        '''

        if angle > 337.5 or angle <= 22.5:
            # North
            direction = "north"
        elif angle > 22.5 and angle <= 67.5:
            # North-East
            direction = "north_east"
        elif angle > 67.5 and angle <= 112.5:
            # East
            direction = "east"
        elif angle > 112.5 and angle <= 157.5:
            # South-East
            direction = "south_east"
        elif angle > 157.5 and angle <= 202.5:
            # South
            direction = "south"
        elif angle > 202.5 and angle <= 247.5:
            # South-West
            direction = "south_west"
        elif angle > 247.5 and angle <= 292.5:
            # West
            direction = "west"
        else:
            # North-West
            direction = "north_west"

        return direction
