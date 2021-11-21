import uuid
from os import stat

import ezdxf
import shapely.geometry as geom
from app.main.constants import *
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.models.line import Line
from app.main.models.point import Point
from app.main.models.polygon import Polygon
from app.main.models.wall import Wall
from app.main.services.validation_helper import ValidationHelper
from app.main.services.walls_extraction import WallsExtraction
from area import area
from ezdxf.document import Drawing
from ezdxf.entities.lwpolyline import LWPolyline
from ezdxf.layouts.layout import Modelspace
from loguru import logger
from shapely.geometry import LineString
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon

'''
Description: This class contains any helper logic of the extraction process and is partly integrated from prototype c
'''

main_logger = logger.bind()

class ExtractionHelper:

    @staticmethod
    def get_all_annotations(model: Modelspace, layer: str) -> list[list]:
        '''
        Description: Method to get all annotations for a specific layer like 'RAUMSTEMPEL'
        Params: model: Modelspace, layer: str
        Return: annotation: list[list]
        '''
        result = []
        if not isinstance(model, Modelspace):
            main_logger.warning('Parameter is not a Modelspace object at getting all annotations for layer {}'.format(
                str(layer)))
            result = None
        else:
            annotations = [i for i in model.query(
                'INSERT[layer=="{}"]'.format(layer))]
            for annotation in annotations:
                annotation_list = []
                valid_annotation = True
                for attribute in annotation.attribs:
                    annotation_attributes = (
                        attribute.dxf.tag, attribute.dxf.text, attribute.dxf.insert[0], attribute.dxf.insert[1])
                    if (attribute.dxf.tag == NUDATA_ATTRIBUTE_RAUMNUMMER or attribute.dxf.tag == NUDATA_ATTRIBUTE_RAUMBEZEICHNUNG) and attribute.dxf.text == '':
                        valid_annotation = False
                    else:
                        annotation_list.append(annotation_attributes)
                if valid_annotation:
                    result.append(annotation_list)
        return result

    @staticmethod
    def calculate_perimeter_with_arcs(substituted_boundary_lines_with_arcs: list) -> float:
        '''
        Description: Method to calculate perimeter for boundary lines (normal lines and lines representing arcs)
        Params: substituted_boundary_lines_with_arcs: list
        Return: result: float
        '''
        result = 0.0
        if type(substituted_boundary_lines_with_arcs) != list:
            main_logger.warning('Parameter is not a list at calculating perimeter for boundary lines')
            return None
        for line in substituted_boundary_lines_with_arcs:
            if type(line) != dict:
                main_logger.warning(
                    'Line list has to contain dict objects at calculating perimeter for boundary lines')
                return None
            elif list(line.keys()) != ['line', 'length']:
                main_logger.warning(
                    'Line dict has to have following keys: line, length at calculating perimeter for boundary lines')
                return None
            result = result + line['length']
        return result

    @staticmethod
    def get_lines_of_polygon(polygon_points: list) -> list[dict]:
        '''
        Description: Method to get lines and distance of polygons
        Params: polygon_points: list
        Return: result: list[dict]
        '''
        result = []
        line = None
        i = 0
        if not type(polygon_points) == list:
            main_logger.warning(
                'Parameter polygon_points is not a list at getting lines and distance of polygon')
            return None
        elif not polygon_points:
            return None
        elif len(polygon_points) <= 2:
            main_logger.warning('Parameter polygon_points must have more than two points for getting lines and distance of a valid '
                  'polygon Polygon.')
            return None
        for point in polygon_points:
            if i < (len(polygon_points) - 1):
                line = LineString([point, polygon_points[i + 1]])
            elif i == (len(polygon_points) - 1):
                line = LineString([point, polygon_points[0]])
            if line is not None:
                result.append(
                    {'coords': list(line.coords), 'length': line.length})
            i += 1
        return result

    @staticmethod
    def has_inner_points(room_coords: list, whole_room: ShapelyPolygon) -> bool:
        '''
        Description: Method, to check if a polygon has inner points
        Params: room_coords: list, whole_room: ShapelyPolygon
        Return: result: bool
        '''
        all_points = []
        for coord in room_coords:
            all_points.append(ShapelyPoint(coord))
        for point in all_points:
            if ExtractionHelper.check_points_as_polygon(whole_room, point) is True \
                    or ExtractionHelper.check_point(whole_room, point) is True:
                return True
        return False

    @staticmethod
    def check_points_as_polygon(polygon: ShapelyPolygon, point: ShapelyPoint) -> bool:
        '''
        Description: Method to check if a point is in a polygon
            - creates 4 new Points and a Polygon around the original Point
            - checks if the new Polygon is inside the passed Polygon using shapely´s 'contains'-method
        Params: polygon: ShapelyPolygon, point: ShapelyPoint
        Return: result: bool
        '''
        check_distance = 0.1
        point_polygon = ShapelyPolygon([(point.x + check_distance, point.y),
                                        (point.x, point.y + check_distance),
                                        (point.x - check_distance, point.y),
                                        (point.x, point.y - check_distance)])

        return polygon.contains(point_polygon)

    @staticmethod
    def check_point(polygon: ShapelyPolygon, point: ShapelyPoint) -> bool:
        '''
        Description: Method to check if a point is in a polygon
            - creates 4 new Points around the original Point
            - checks if the all the 4 Points are inside the passed Polygon using shapely´s 'contains'-method
        Params: polygon: ShapelyPolygon, point: ShapelyPoint
        Return: result: bool
        '''
        contains_x1 = False
        contains_x2 = False
        contains_y1 = False
        contains_y2 = False
        check_distance = 1
        x1 = ShapelyPoint(point.x + check_distance, point.y)
        if polygon.contains(x1):
            contains_x1 = True
        x2 = ShapelyPoint(point.x - check_distance, point.y)
        if polygon.contains(x2):
            contains_x2 = True
        y1 = ShapelyPoint(point.x, point.y + check_distance)
        if polygon.contains(y1):
            contains_y1 = True
        y2 = ShapelyPoint(point.x, point.y - check_distance)
        if polygon.contains(y2):
            contains_y2 = True
        return contains_x1 is True and contains_x2 is True and contains_y1 is True and contains_y2 is True

    @staticmethod
    def separate_inner_points(room_coords: list, whole_room: ShapelyPolygon) -> dict:
        '''
        Description: Method, to separate boundary points from inner points, compared to a polygon
        Params: room_coords: list, whole_room: ShapelyPolygon
        Return: result: dict
        '''
        result = dict()
        all_points = []
        for coord in room_coords:
            all_points.append(ShapelyPoint(coord))
        inner_points = []
        outer_points = []

        for point in all_points:
            if ExtractionHelper.check_points_as_polygon(whole_room, point) is True \
                    or ExtractionHelper.check_point(whole_room, point) is True:
                inner_points.append(
                    ValidationHelper.get_coords_of_point(point))
            else:
                outer_points.append(
                    ValidationHelper.get_coords_of_point(point))
        result['outer_points'] = outer_points
        result['inner_points'] = inner_points
        return result

    @staticmethod
    def get_modelspace(dxf_file: Drawing) -> Modelspace:
        '''
        Description: This method extracts the modelspace of a Drawing
        Params: model: Modelspace
        Return: modelspace: Modelspace
        '''
        if not isinstance(dxf_file, Drawing) or dxf_file is None:
            main_logger.critical("unable to get_modelspace() from dxf_file")
            raise RuntimeWarning("modelspace not found")
        else:
            main_logger.success("sucessfully get_modelspace() from dxf_file: {}".format(dxf_file))
            return dxf_file.modelspace()

    @staticmethod
    def get_outline_polygon(model: Modelspace) -> Polygon:
        '''
        Description: This method extracts the outline polygon of a simple plan
        Params: model: Modelspace
        Return: outline_polygon: Polygon
        '''
        main_logger.debug("get_outline_polygon for modelspace: {}".format(model))
        bgf_polylines = model.query('LWPolyline[layer=="{}"]'.format(NUDATA_LAYER_BGF))
        bgf_polyline = bgf_polylines[0]
        polygon_id = str(uuid.uuid1())
        coordinates = bgf_polyline.get_points("XY")
        if len(coordinates) > 2:
            points = []
            for coordinate in coordinates:
                point = ExtractionHelper.get_point_from_coordinate(coordinate)
                points.append(point)

            area, perimeter = ExtractionHelper.get_area_and_perimeter_from_polyline(
                bgf_polyline)
            outline_polygon = Polygon(polygon_id, area, perimeter, False)
            outline_polygon.points = points
            return outline_polygon

        return None

    @staticmethod
    def get_point_from_coordinate(coordinate: tuple) -> Point:
        '''
        Description: This method creates a point from coordinates with x and y
        Params: coordinate: tuple
        Return: point: Point
        '''
        x_coordinate = coordinate[0]
        y_coordinate = coordinate[1]
        return Point(x_coordinate, y_coordinate)

    @staticmethod
    def get_point_from_seb_coordinate(coordinate: tuple) -> Point:
        '''
        Description: This method creates a point from coordinates with x, y, s, e and b
        Params: coordinate: tuple
        Return: point: Point
        '''
        x_coordinate = coordinate[0]
        y_coordinate = coordinate[1]
        s_width = coordinate[2]
        e_width = coordinate[3]
        b_value = coordinate[4]
        if not b_value:
            b_value = 0.0
        if not e_width:
            e_width = 0.0
        if not s_width:
            s_width = 0.0
        point = Point(x_coordinate, y_coordinate)
        point.s_width = s_width
        point.e_width = e_width
        point.b_value = b_value
        return point

    @staticmethod
    def get_area_and_perimeter_from_polyline(polyline: LWPolyline) -> tuple[float, float]:
        '''
        Description: This method calculates area and perimeter from a polyline.
        Params: polyline: LWPolyline
        Return: area: float, perimeter: float
        '''
        if type(polyline) != LWPolyline:
            main_logger.debug('Parameter ist not LWPolyline - can not calculate area and perimeter')
            return None
        if len(polyline) > 2:
            polygon = ShapelyPolygon(polyline.get_points("XY"))
            area = polygon.area

            polygon_points = []
            for point in polyline.get_points('XY'):
                polygon_points.append(point)

            perimeter = ExtractionHelper.calculate_perimeter(polygon_points)

            return area, perimeter

    @staticmethod
    def calculate_perimeter(polygon_points: list) -> float:
        '''
        Description: Method to calculate perimeter
        Params: polygon_points: list
        Return: perimeter: float
        '''
        result = 0.0
        if not type(polygon_points) == list:
            main_logger.warning('Parameter is not a list of points at calculating perimeter of polygon')
            return None
        elif not polygon_points:
            main_logger.warning('Polygon point list is empty at calculating perimeter of polygon')
            return None
        elif len(polygon_points) <= 2:
            main_logger.warning(
                'The polygon have more than two points at calculating perimeter of polygon')
            return None
        else:
            lines_list = ExtractionHelper.get_lines_of_polygon(
                polygon_points=polygon_points)
            for line in lines_list:
                result = result + line['length']
            return result

    @staticmethod
    def transform_polygon_to_shapely_polygon(polygon: Polygon) -> ShapelyPolygon:
        '''
        Description: This method transforms a polygon to a shapely polygon
        Params: polygon: Polygon
        Return: shapely_polygon: ShapelyPolygon
        Exception: ---
        '''
        points = polygon.points
        coordinates = []
        for point in points:
            my_tuple = (point.x_coordinate, point.y_coordinate)
            coordinates.append(my_tuple)

        shapely_polygon = ShapelyPolygon(coordinates)
        return shapely_polygon

    @staticmethod
    def transform_points_to_shapely_polygon(points: list[Point]) -> ShapelyPolygon:
        '''
        Description: This method transforms a list of points to a shapely polygon.
        Params: points: list[Point]
        Return: shapely_polygon: ShapelyPolygon
        '''
        coordinates = []
        for point in points:
            my_tuple = (point.x_coordinate, point.y_coordinate)
            coordinates.append(my_tuple)

        shapely_polygon = ShapelyPolygon(coordinates)
        return shapely_polygon

    @staticmethod
    def transform_polygon_to_line_string(polygon: Polygon) -> LineString:
        """
        Description: This method transforms a polygon into a linestring
        Params: polygon: Polygon
        Return: line_string: LineString
        """
        coordinates = polygon.points
        point_list = []
        for coordinate in coordinates:
            point = geom.Point(coordinate.x_coordinate,
                               coordinate.y_coordinate)
            point_list.append(point)

        line_string = geom.LineString(point_list)
        return line_string

    def transform_wall_to_line_string(wall: Wall) -> LineString:
        """
        Description: This method transforms a wall into a linestring
        Params: wall: Wall
        Returns: line_string: LineString
        Exception: Exception
        """
        if(not wall.start_point and not wall.end_point):
            raise Exception("Wall not fully defined {}".format(str(wall)))
        line_string = geom.LineString(
            [(wall.start_point.x_coordinate, wall.start_point.y_coordinate), (wall.end_point.x_coordinate, wall.end_point.y_coordinate)])
        return line_string

    @staticmethod
    def remove_loops_from_outline_polygon(outline_polygon: Polygon, range: int) -> Polygon:
        '''
        Description: This method is used to identify and remove loops in outline polygon. 
            As a result elevator will no be detected as outerwall (improved outerwall and orientation)
        Params: outline_polygon: Polygon, range: int
        Return: outline_polygon: Polygon
        '''
        point_index = 0
        try:
            for point in outline_polygon.points:
                i = 1
                while i < range:
                    distance = WallsExtraction.get_distance_of_points(point, outline_polygon.points[point_index + i])
                    if distance < 0.0001:
                        del outline_polygon.points[point_index + 1: point_index + i]
                    i += 1
                point_index += 1
        except IndexError:
            pass # IndexError at the end of outline_polygon
        return outline_polygon

    @staticmethod
    def create_linestring_from_wall(wall: Wall) -> LineString:
        '''
        Description: This method creates a linestring from a wall.
        Params: wall: Wall
        Return: line: LineString
        Exception: ---
        '''
        line = LineString([(wall.start_point.x_coordinate, wall.start_point.y_coordinate),(wall.end_point.x_coordinate, wall.end_point.y_coordinate)])
        return line


    @staticmethod
    def get_architecture_polylines(plan: ExtractionRequestFile, layer: str) -> list[LWPolyline]:
        '''
        Description: This method gets all polylines from an architecture plan.
        Params: linestrings_tragwand: list, linestrings_leichtwand: list
        Return:  architecture_polylines: list[LWPolyline]
        Exception: ---
        '''
        dxf_file = ezdxf.readfile(plan.file_path + plan.file_name)
        md = dxf_file.modelspace()
        architecture_polylines = md.query("LWPolyline[layer=='{}']".format(layer))
        return architecture_polylines

    @staticmethod
    def create_linestring_from_polyline(polyline: LWPolyline) -> list[LineString]:
        '''
        Description: This method creates from one polyline a list of linestrings.
        Params: polyline: LWPolyline
        Return:  linestring_list: list[Linestring]
        Exception: ---
        '''
        linestring_list = []
        xy_coordinates_list = []
        index = 0
        for x in polyline:
            x_value = x[0]
            y_value = x[1]
            coordinate = (x_value, y_value)
            xy_coordinates_list.append(coordinate)
        for index in range(len(xy_coordinates_list)-1):
            line = LineString([xy_coordinates_list[index] , xy_coordinates_list[index+1]])
            linestring_list.append(line)
        return linestring_list

    @staticmethod
    def get_line_string_of_two_coordinates(coordinate_1: tuple, coordinate_2: tuple) -> LineString:
        '''
        Description: This method creates a line string from two coordinates
        Params: coordinate_1: tuple, coordinate_2: tuple
        Return: line_string: LineString
        '''
        return LineString([(coordinate_1[0], coordinate_1[1]), (coordinate_2[0], coordinate_2[1])])

    @staticmethod
    def get_line_from_coordinates(coordinate_1: tuple, coordinate_2: tuple) -> Line:
        '''
        Description: This method creates a line instance from two coordinates
        Params: coordinate_1: tuple, coordinate_2: tuple
        Return: line: Line
        '''
        line_string = ExtractionHelper.get_line_string_of_two_coordinates(coordinate_1, coordinate_2)
        start_point = ExtractionHelper.get_point_from_coordinate(coordinate_1)
        end_point = ExtractionHelper.get_point_from_coordinate(coordinate_2)
        return Line("", line_string, start_point=start_point, end_point=end_point)

    @staticmethod
    def create_lines_from_polylines(polylines: list[LWPolyline]) ->list[Line]:
        '''
        Description: This method creates lines from a list of polylines
        Params: polylines: list[LWPolyline]
        Returns: lines: list[Line]
        '''
        lines = []
        for polyline in polylines:
            for i in range(len(polyline)-1):
                line = ExtractionHelper.get_line_from_coordinates(polyline[i], polyline[i + 1])
                lines.append(line)
        return lines

    @staticmethod
    def create_line_from_two_points(start_point: Point, end_point: Point) -> Line:
        '''
        Description: This method creates a line from two points
        Params: start_point: Point, end_point: Point
        Returns: line: Line
        '''
        line_string = ExtractionHelper.create_line_string_of_two_points(start_point, end_point)
        return Line("id", line_string, start_point=start_point, end_point=end_point)

    @staticmethod
    def create_line_string_of_two_points(point_1: Point, point_2: Point)-> LineString:
        '''
        Description: This method creates a linestring out of two points
        Params: point_1: Point, point_2: Point
        Return: line_string: LineString
        '''
        return LineString([(point_1.x_coordinate, point_1.y_coordinate), (point_2.x_coordinate, point_2.y_coordinate)])

    @staticmethod
    def get_length_between_points(point_1: Point, point_2: Point) -> float:
        '''
        Description: This method calculates the length between two points
        Params: point_1: Point, point_2: Point
        Return: length: float
        '''
        line_string = LineString([(point_1.x_coordinate, point_1.y_coordinate), (point_2.x_coordinate, point_2.y_coordinate)])
        return line_string.length

