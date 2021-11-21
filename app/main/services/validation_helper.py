
from threading import Condition

import ezdxf
from app.main.constants import *
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from ezdxf.entities.lwpolyline import LWPolyline
from loguru import logger
from shapely.geometry import LineString, MultiLineString, Point, Polygon

round_decimals = 5  # 3,4,5 all cut 2 lines (from 12 to 10)

'''
Description: This class contains the logic to validate various data and is partly integrated from prototype c.
'''

main_logger = logger.bind()

class ValidationHelper:

    @staticmethod
    def check_if_polygon_was_recreated(coords: list, room_name: str):
        '''
        Description: Method to check if the passed coords can be formed into a polygon
        Params: coords: list, room_name: str
        Return: polygon: Polygon
        '''
        try:
            polygon = Polygon(coords)
            return polygon
        except:
            main_logger.warning('could not recreate' + room_name)
            return None


    @staticmethod
    def get_lines_of_polygon(polygon_points: list[tuple]) -> list[dict]:
        '''
        Description: Method to get lines and distance of polygons
        Params: polygon_points: list[tuple]
        Return: list[dict]
        '''
        result = []
        line = None
        i = 0
        if not type(polygon_points) == list:
            main_logger.warning('unable to get_lines_of_polygon because parameter: {} is not a list'.format(type(polygon_points)))
            return None
        elif not polygon_points:
            main_logger.warning('unable to get_lines_of_polygon because parameter list is empty')
            return None
        elif len(polygon_points) <= 2:
            main_logger.info('unable to get_lines_of_polygon because a polygon must have more than two points')
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
    def get_line_objects_of_polygon(polygon_points: list[tuple]) -> list[LineString]:
        '''
        Description: Method to get line objects of polygons
        Params: polygon_points: list[tuple]
        Return: list[LineString]
        '''
        result = []
        i = 0
        if not type(polygon_points) == list:
            main_logger.warning('unable to get_line_objects_of_polygon because parameter: {} is not a list.'.format(type(polygon_points)))
            return None
        elif not polygon_points:
            main_logger.warning('unable to get_line_objects_of_polygon because parameter list is empty')
            return None
        elif len(polygon_points) <= 2:
            main_logger.warning('unable to get_line_objects_of_polygon because a polygon must have more than two points')
            return None
        for point in polygon_points:
            if i < (len(polygon_points) - 1):
                result.append(LineString([point, polygon_points[i + 1]]))
            elif i == (len(polygon_points) - 1):
                result.append(LineString([point, polygon_points[0]]))
            i += 1
        return result

    @staticmethod
    def substitute_boundary_lines_with_arcs(boundary_line_list_polygon: list, virt_arc_list_with_length: list) -> list[dict]:
        '''
        Description: Method to substitute boundary lines of a polygon with extracted arcs
        Params: boundary_line_list_polygon: list, virt_arc_list_with_length: list
        Return: result: list[dict]
        '''
        result = []
        if not type(boundary_line_list_polygon) == list or not type(virt_arc_list_with_length) == list:
            main_logger.warning("unable to substitute_boundary_lines_with_arcs because {} and/or {} != list".format(type(boundary_line_list_polygon), type(virt_arc_list_with_length)))
            return None
        else:
            for boundary_line in boundary_line_list_polygon:
                matching_success = False
                if type(boundary_line) != LineString:
                    main_logger.warning('unable to substitute_boundary_lines_with_arcs because boundary_lines: {} have to be LineString objects'.format(type(boundary_line)))
                    return None
                boundary_line_points = list(boundary_line.coords)
                for virt_arc in virt_arc_list_with_length:
                    if type(virt_arc) != dict:
                        main_logger.warning('unable to substitute_boundary_lines_with_arcs because virt_arc: {} have to be dict objects'.format(type(virt_arc)))
                        return None
                    elif list(virt_arc.keys()) != ['arc', 'length']:
                        main_logger.warning('unable to substitute_boundary_lines_with_arcs because virt_arc dict requires keys arc & length. got: {}'.format(list(virt_arc.keys())))
                        return None
                    virt_arc_points = list(virt_arc['arc'].coords)
                    if Point(boundary_line_points[0]).almost_equals(Point(virt_arc_points[0]), decimal=4) and \
                            Point(boundary_line_points[1]).almost_equals(Point(virt_arc_points[len(virt_arc_points) - 1]),
                                                                         decimal=4):
                        result.append(
                            {'line': virt_arc['arc'], 'length': virt_arc['length']})
                        matching_success = True
                        break
                if not matching_success:
                    result.append(
                        {'line': boundary_line, 'length': boundary_line.length})
            return result

    @staticmethod
    def get_coords_of_point(point: Point) -> tuple:
        '''
        Description: Method to get x and y coordinates of Point as tuple
        Params: point: Point
        Return: coords: tuple
        '''
        if not isinstance(point, Point):
            main_logger.warning('unable to get_coords_of_point because parameter: {} is != Point'.format(type(Point)))
            return None
        else:
            return (point.x, point.y)

    @staticmethod
    def get_coords_from_line_list(lines: list[dict]) -> list[tuple]:
        '''
        Description: Method to get x and y coordinates as tuple of a list of lines
        Params: lines: list[dict]
        Return: result: list[tuple]
        '''
        result = []
        if list(lines[0].keys()) == ['line']:
            for line in lines:
                for coord in line['line']['coords']:
                    result.append(coord)
        if list(lines[0].keys()) == ['coords', 'length']:
            for line in lines:
                for coord in line['coords']:
                    result.append(coord)
        else:
            main_logger.warning('unable to get_coords_from_line_list because passed list of lines is not supported')
            return None
        return result


    @staticmethod
    def create_polygon(line_list: list[dict]) -> Polygon:
        '''
        Description: Method to create polygon of a list of lines
        Params: line_list: list[dict]
        Return: polygon: Polygon
        '''
        if not type(line_list) == list:
            main_logger.warning('unable to create_polygon because parameter: {} is != list'.format(type(line_list)))
            return None
        elif not line_list:
            main_logger.warning('unable to create_polygon because line_list is empty')
            return None
        else:
            polygon_points = []
            for line in line_list:
                if not type(line) == dict:
                    main_logger.warning('unable to create_polygon because line {} is != dict'.format(type(line)))
                    return None
                elif not ['coords', 'length'] == list(line.keys()):
                    main_logger.warning('unable to create_polygon because list should only contain line dictionaries with keys coords and length. got: {}'.format(list(line.keys())))
                    return None
                else:
                    for point in line['coords']:
                        if line_list.index(line) == 0:
                            polygon_points.append(point)
                        elif line_list.index(line) == len(line_list):
                            polygon_points.append(point)
                        elif point not in polygon_points:
                            polygon_points.append(point)
            return Polygon(polygon_points)

    @staticmethod
    def create_MultiLineString(line_list: list[dict]):
        '''
        Description: Method to create MultiLineString of a list of line objects
        Params: line_list: list[dict]
        Return: multi_line_string: MultiLineString
        '''
        if not type(line_list) == list:
            main_logger.warning('unable to create_MultiLineString because parameter: {} is != list'.format(type(line_list)))            
            return None
        elif not line_list:
            main_logger.warning('unable to create_MultiLineString because line_list is empty')
            return None
        else:
            for line in line_list:
                if not isinstance(line, LineString):
                    main_logger.warning('unable to create_MultiLineString because list should only contain LineStrings.')
                    return None
            return MultiLineString(line_list)

    @staticmethod
    def create_LineString(coordinate_list: list[tuple]) -> LineString:
        '''
        Description: Method to create LineString of a list of coordinates
        Params: coordinate_list: list[tuple]
        Return: line_string: LineString
        '''
        if not type(coordinate_list) == list:
            main_logger.warning('unable to create_LineString because parameter: {} is != list'.format(type(coordinate_list)))            
            return None
        elif not coordinate_list:
            main_logger.warning('unable to create_LineString because line_list is empty')
            return None
        else:
            return LineString(coordinate_list)

    @staticmethod
    def cut_duplicates_from_list(list_to_filter: list) -> list:
        '''
        Description: Method to cut duplicates from a list
        Params: list_to_filter: list
        Return: uniq: list
        '''
        seen = set()
        uniq = []
        for x in list_to_filter:
            if x not in seen:
                seen.add(x)
                uniq.append(x)
        return uniq

    @staticmethod
    def get_duplicates_from_list(list_to_filter: list) -> list:
        '''
        Description: Method to get (only) duplicates from a list
        Params: list_to_filter: list
        Return: dupls: list
        '''
        seen = set()
        dupls = []
        for x in list_to_filter:
            if x not in seen:
                seen.add(x)
            else:
                dupls.append(x)
        return dupls

    @staticmethod
    def remove_all_duplicates_from_list(list_to_filter: list):
        '''
        Description: Method to check for duplicates and remove all non-unique items from a list
        Params: list_to_filter: list
        Return: uniq: list
        '''
        seen = set()
        uniq = []
        for x in list_to_filter:
            if x not in seen:
                seen.add(x)
                uniq.append(x)
            else:
                try:
                    uniq.remove(x)
                except ValueError:
                    pass
        return uniq


    @staticmethod
    def double_check_length(line: dict) -> dict:
        '''
        Description: Method to check if the length of a line is correct, by calculating it with shapely LineString.length
        Params: line: dict
        Return: result: dict
        '''
        result = {}
        original_length = line['length']
        new_line = LineString(line['coords'])
        new_length = new_line.length
        if new_length == original_length:
            return line
        else:
            main_logger.debug('double_check_length: new_length: {} | original_length: {}'.format(new_length, original_length))
            result['coords'] = line['coords']
            result['length'] = new_length
            return result

    @staticmethod
    def make_single_lines(all_coords: list) -> list[dict]:
        '''
        Description: Method to separate a list of coords into a list of lines connecting the points subsequently
        Params: all_coords: list
        Return: result: list[dict]
        '''
        result = []
        adjusted_lines_to_plot = []
        for i in range(1, len(all_coords)):
            tmp_lineString = LineString([all_coords[i - 1], all_coords[i]])
            adjusted_lines_to_plot.append(tmp_lineString)
            tmp_len = tmp_lineString.length 
            result.append(
                {'coords': [all_coords[i - 1], all_coords[i]], 'length': tmp_len})
        return result

    @staticmethod
    def get_uniq_coords_from_lines(lines: list) -> list[tuple]:
        '''
        Description: Method to get unique coordinates from list of lines
        Params: lines: list
        Return: result: list[tuple]
        '''
        all_coords = []
        for line in lines:
            for coord in line['coords']:
                all_coords.append(coord)
        i = 0
        x = len(all_coords)
        while i < x:
            point_1 = Point(all_coords[i])
            point_2 = Point(all_coords[i - 1])

            if point_1.almost_equals(point_2, decimal=4):
                all_coords.pop(i)
                x = x - 1
            else:
                i = i + 1
        return all_coords

    @staticmethod
    def get_duplicated_lines(lines: list) -> list[dict]:
        '''
        Description: Method to get duplicated lines (with the same length) from a polygon. 
            USE CASE: only for showing / checking which lines are cut from a polygon
        Params: lines: list
        Return: result: list[dict]
        '''
        result = []
        lengths = []
        for line in lines:
            length = line['length']
            if length != 0.0:
                lengths.append(round(length, round_decimals))
        rounded_lengths = ValidationHelper.get_duplicates_from_list(lengths)
        for line in lines:
            if round(line['length'], round_decimals) in rounded_lengths:
                result.append(line)
        return result

    @staticmethod
    def round_coord(coord: tuple) -> tuple:
        '''
        Description: Method to round both x and y values of a coord
        Params: coord: tuple
        Return: coord: tuple
        '''
        x = round(coord[0], round_decimals)
        y = round(coord[1], round_decimals)
        return x, y


    @staticmethod
    def check_scaling(simple_plan: ExtractionRequestFile, architecture_plan: ExtractionRequestFile) -> bool:
        '''
        Description: This method checks the scaling of the plans and if they can be matched.
        Params: simple_plan: ExtractionRequestFile, architecture_plan: ExtractionRequestFile
        Return: boolhander: bool
        Exception: ---
        '''

        condition1 = False
        condition2 = False
        condition3 = False
        
        simple_polygons= ValidationHelper.get_simple_polylines(simple_plan) # auslesen der polygons
        architecture_polygons= ValidationHelper.get_architecture_polylines(architecture_plan) #auslesen der architecture_polygons

        min_value_simple = ValidationHelper.filter_coordinates(simple_polygons, 'MIN')
        max_value_simple = ValidationHelper.filter_coordinates(simple_polygons, 'MAX')

        point_min_simple = Point(min_value_simple[0], min_value_simple[1])
        point_max_simple = Point(max_value_simple[0], max_value_simple[1])

        distance_simple = point_min_simple.distance(point_max_simple)

        min_value_architecture = ValidationHelper.filter_coordinates(architecture_polygons, 'MIN')
        max_value_architecture = ValidationHelper.filter_coordinates(architecture_polygons, 'MAX')

        point_min_architecture = Point(min_value_architecture[0], min_value_architecture[1])
        point_max_architecture = Point(max_value_architecture[0], max_value_architecture[1])

        distance_architecture = point_min_architecture.distance(point_max_architecture)

        factor = distance_simple/distance_architecture
        
        if( MATCHING_SCALE_THRESHOLD["LOWER"] <= factor <= MATCHING_SCALE_THRESHOLD["UPPER"]):
            condition1 = True
        if condition1 and ENABLE_CUSTOM_OFFSET:
            main_logger.info("Enabled custom offset")
            return True
        offset_value_x = point_min_simple.x - point_min_architecture.x
        offset_value_y = point_min_simple.y - point_min_architecture.y
        main_logger.info("X Offset: {}".format(str(offset_value_x)))
        main_logger.info("Y Offset: {}".format(str(offset_value_y)))

        if((offset_value_x == FIRST_LEVEL_X_OFFSET_VALIDATION and offset_value_y == FIRST_LEVEL_Y_OFFSET_VALIDATION) 
        or (offset_value_x == SECOND_LEVEL_X_OFFSET_VALIDATION and offset_value_y == SECOND_LEVEL_Y_OFFSET_VALIDATION)
        or (offset_value_x == GROUND_LEVEL_X_OFFSET_VALIDATION and offset_value_y == GROUND_LEVEL_Y_OFFSET_VALIDATION)):
            condition2 = True
        
        if((MATCHING_OFFSET_THRESHOLD["LOWER"] <= offset_value_x <= MATCHING_OFFSET_THRESHOLD["UPPER"]) and 
        (MATCHING_OFFSET_THRESHOLD["LOWER"] <= offset_value_y <= MATCHING_OFFSET_THRESHOLD["UPPER"])):
            condition3 = True
            
        return condition1 and (condition2 or condition3)

    def filter_coordinates(simple_polylines: list, filter_aim: str) -> tuple:
        '''
        Description: This method finds den min/max value of each Koordinate tuple list.
        Params: simple_polylines: list, filter_aim: str
        Return: item: tuple
        Exception: ---
        '''
        coordinates = ValidationHelper.create_coordinates_list(simple_polylines) 
        if filter_aim == 'MIN':
            item=min(coordinates, key=lambda n: n[0])
            return item
        if filter_aim == 'MAX':
            item=max(coordinates, key=lambda n: n[0])
            return item

    def create_coordinates_list(polylines: list) -> list[tuple]:
        '''
        Description: This method creates a list of coordinates from a list of polylines.
        Params: polylines: list
        Return: coordinates: list[tuple]
        Exception: ---
        '''
        coordinates = []
        for x in polylines:
            for y in x:
                coordinates.append(y)
        return coordinates

    def get_simple_polylines(plan: ExtractionRequestFile) -> list[LWPolyline]:
        '''
        Description: This method gets all simple plan polylines from an given ExtractionRequestFile object.
        Params: plan: ExtractionRequestFile
        Return: polylines: list[LWPolyline]
        Exception: ---
        '''
        polylines = []
        dxf_file = ezdxf.readfile(plan.file_path + plan.file_name)
        md = dxf_file.modelspace()
        polylines = md.query("LWPolyline[layer=='{}']".format(NUDATA_LAYER_RAUMPOLYGON))
        return polylines

    def get_architecture_polylines(plan: ExtractionRequestFile) -> list[LWPolyline]:
        
        '''
        Description: This method gets all architecture plan polylines for specific layer from an given ExtractionRequestFile object.
        Params: plan: ExtractionRequestFile
        Return: architecture_polylines: List[LWPolyline]
        Exception: ---
        '''
        dxf_file = ezdxf.readfile(plan.file_path + plan.file_name)
        md = dxf_file.modelspace()
        leichtwand_polylines = md.query("LWPolyline[layer=='{}']".format(LIGHT_WALL_LAYER))
        tragwand_polylines = md.query("LWPolyline[layer=='{}']".format(LOAD_BEARING_WALL_LAYER))
        architecture_polylines = []
        for x in leichtwand_polylines:
            architecture_polylines.append(x)
        for x in tragwand_polylines:
            architecture_polylines.append(x)
        return architecture_polylines
