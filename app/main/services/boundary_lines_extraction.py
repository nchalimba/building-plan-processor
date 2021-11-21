from app.main.services.validation_helper import ValidationHelper
from loguru import logger
from shapely.geometry import LineString, Point

round_decimals = 8
main_logger = logger.bind()

'''
Description: This class contains the logic of prototype c to calculate boundary lines
'''

class BoundaryLinesExtraction:
    @staticmethod
    def recreate_missing_lines(lines: list[dict], room_name: str) -> dict:
        '''
        Description: Method to recreate missing lines in a polygon, by "re-connecting" the points.
        Params: lines: list[dict], room_name: str
        Return: result: dict
        '''
        adjusted_lines_to_plot = []
        result = []
        all_coords = ValidationHelper.get_uniq_coords_from_lines(lines)
        for i in range(0, len(all_coords)):
            tmp_lineString = LineString(
                [all_coords[i - 1], all_coords[i]])  
            adjusted_lines_to_plot.append(tmp_lineString)
            tmp_len = tmp_lineString.length 
            result.append( 
                {"coords": [tmp_lineString.coords[0], tmp_lineString.coords[-1]],
                 "length": tmp_len})

        return result

    @staticmethod
    def substitute_boundary_lines_with_arcs(boundary_line_list_polygon: list, virt_arc_list_with_length: list) -> dict:
        '''
        Description: Method to replace simple "recreated" lines with the correct "arc"-lines
        Params: boundary_line_list_polygon: list, virt_arc_list_with_length: list
        Return: result: dict
        '''
        result = []
        if not type(boundary_line_list_polygon) == list or not type(virt_arc_list_with_length) == list:
            return None
        else:
            for boundary_line in boundary_line_list_polygon:
                matching_success = False
                if type(boundary_line) != dict:
                    main_logger.warning("Boundary lines have to be have to be dict objects. "
                          "(Method: substitute_boundary_lines_with_arcs | in validation.boundary_lines)")
                    return None
                boundary_line_points = boundary_line["coords"]
                for virt_arc in virt_arc_list_with_length:
                    if type(virt_arc) != dict:
                        main_logger.warning("Objects in list of virtual arcs have to be dict objects. "
                              "(Method: substitute_boundary_lines_with_arcs | in validation.boundary_lines)")
                        return None
                    virt_arc_points = virt_arc["coords"]
                    line_start_p = Point(boundary_line_points[0])
                    arc_start_p = Point(virt_arc_points[0])
                    line_end_p = Point(boundary_line_points[1])
                    arc_end_p = Point(virt_arc_points[-1])
                    decimal = 4
                    if line_start_p.almost_equals(arc_start_p, decimal=decimal) and \
                            line_end_p.almost_equals(arc_end_p, decimal=decimal) \
                            or line_start_p.almost_equals(arc_end_p, decimal=decimal) and \
                            line_end_p.almost_equals(arc_start_p, decimal=decimal):
                        split_arc_lines = ValidationHelper.make_single_lines(virt_arc_points)
                        for line in split_arc_lines:
                            result.append(line)
                        matching_success = True
                        virt_arc_list_with_length.remove(virt_arc)
                        break
                if not matching_success:
                    result.append(boundary_line)
            return result

    @staticmethod
    def get_boundary_lines(lines: list[dict], arcs: list[dict], room_name: str) -> dict:
        '''
        Description: Method to remove duplicated lines (with the same length) from a polygon
        Params: lines: list[dict], arcs: list[dict], room_name: str
        Return: result: dict
        '''
        result = BoundaryLinesExtraction.cut_duplicated_lines_by_length_and_point_distance(
            lines, room_name)
        result = BoundaryLinesExtraction.recreate_missing_lines(
            result, room_name)
        if not len(arcs) == 0:
            result = BoundaryLinesExtraction.substitute_boundary_lines_with_arcs(
                result, arcs)
        return result


    @staticmethod
    def check_start_end_points(line: dict, lines_to_check: list[dict]) -> bool:
        '''
        Description: Method to identify duplicated lines by checking if its points are equal to lines in the list
        Params: line: dict, lines_to_check: list[dict]
        Return: result: bool
        '''
        start_point = Point(line["coords"][0])
        end_point = Point(line["coords"][1])
        for line_2 in lines_to_check:
            start_point_2 = Point(line_2["coords"][0])
            end_point_2 = Point(line_2["coords"][1])
            if start_point.almost_equals(start_point_2) or start_point.almost_equals(end_point_2):
                if end_point.almost_equals(start_point_2) or end_point.almost_equals(end_point_2):
                    return True
        return False

    @staticmethod
    def cut_duplicated_lines_by_length_and_point_distance(lines: list[dict], room_name: str) -> list[dict]:
        '''
        Description: Method to cut duplicate lines
        Params: lines: list[dict], room_name: str
        Return: adjusted_lines: list[dict]
        '''
        lengths = []
        for line in lines:
            ValidationHelper.double_check_length(line)
            length = line["length"]
            if length != 0.0: 
                lengths.append(round(length, round_decimals))

        rounded_lengths = ValidationHelper.remove_all_duplicates_from_list(lengths)
        if rounded_lengths:
            lines_to_check = []
            adjusted_lines = []
            for line in lines:
                if round(line["length"], round_decimals) in rounded_lengths:
                    adjusted_lines.append(line)
                else:
                    lines_to_check.append(line)
            if lines_to_check:
                for line in lines_to_check:
                    if not BoundaryLinesExtraction.check_start_end_points(line,
                                                                          lines_to_check): 
                        adjusted_lines.append(line)

        else: 
            adjusted_lines = lines
        return adjusted_lines
