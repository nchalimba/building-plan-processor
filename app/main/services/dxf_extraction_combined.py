import statistics
import uuid

from app.main.constants import *
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.models.architecture_plan import Architecture_Plan
from app.main.models.architecture_wall import Architecture_Wall
from app.main.models.facade_arc import FacadeArc
from app.main.models.line import Line
from app.main.models.pillar import Pillar
from app.main.models.point import Point
from app.main.models.polygon import Polygon
from app.main.models.simple_plan import Simple_Plan
from app.main.models.wall import Wall
from app.main.models.window import Window
from app.main.reporting.reporting_models import (ExtractedFunctionalities,
                                                 LogMessage)
from app.main.reporting.reporting_service import ReportingService
from app.main.services.dxf_extraction_architecture import \
    DxfExtractionArchitecture
from app.main.services.dxf_extraction_simple import DxfExtractionSimple
from app.main.services.extraction_helper import ExtractionHelper
from ezdxf.document import Drawing
from loguru import logger
from shapely.geometry import LineString
from shapely.geometry import Point as ShapelyPoint
from tqdm import tqdm

'''
Description: This class matches data of a simple plan with data of an architecture plan.
'''
main_logger = logger.bind()
class DxfExtractionCombined:
    
    def entry_point(self, simple_plan: ExtractionRequestFile, simple_dxf_file: Drawing,  architecture_plan: ExtractionRequestFile, architecture_dxf_file: Drawing, level: int) -> tuple[Simple_Plan, Architecture_Plan, ExtractedFunctionalities, list[LogMessage]]:
        '''
        Description: This method is the entry point for every matching order.
        Params: simple_plan: ExtractionRequestFile, simple_dxf_file: Drawing,  
        architecture_plan: ExtractionRequestFile, architecture_dxf_file: Drawing
        Return: simple_plan: Simple_Plan, architecture_plan: Architecture_plan, 
        extracted_functionalities: ExtractedFunctionalities, log_messages: LogMessages
        Exception: ---
        '''
        
        dxf_extraction_simple = DxfExtractionSimple()
        simple_plan, extracted_functionalities_simple, log_messages_simple = dxf_extraction_simple.entry_point(
            simple_plan, simple_dxf_file)

        for polygon in simple_plan.polygons:
            for wall in polygon.walls:
                wall.wall_id = str(uuid.uuid4())

        dxf_extraction_architecture = DxfExtractionArchitecture()
        architecture_plan, extracted_functionalities_architecture, log_messages_architecture, linestrings_list_total = dxf_extraction_architecture.entry_point(architecture_plan, architecture_dxf_file, level)
        main_logger.info("Matching process started")
        simple_plan.polygons, architecture_plan.architecture_walls, wall_log_messages = self.matching_simple_walls_with_polygons(simple_plan.polygons, architecture_plan.architecture_walls)
        simple_plan.polygons, architecture_plan.pillars, pillar_log_messages = self.match_pillars(simple_plan.polygons, architecture_plan.pillars)
        simple_plan.polygons, architecture_plan.windows, window_log_messages = self.match_windows(simple_plan.polygons, architecture_plan.windows)
        simple_plan.polygons, window_length_log_messages = self.calculate_window_length(simple_plan.polygons, architecture_plan.facade_lines, architecture_plan.facade_arcs)
        
        log_messages = log_messages_simple + log_messages_architecture + wall_log_messages + pillar_log_messages + window_log_messages + window_length_log_messages

        extracted_functionalities = self.combine_extracted_functionalities(extracted_functionalities_simple, extracted_functionalities_architecture)

        return simple_plan, architecture_plan, extracted_functionalities, log_messages

    
    def match_pillars(self, simple_polygons: list[Polygon], architecture_pillars: list[Pillar]) ->tuple[list[Polygon], list[Pillar], list[LogMessage]]:
        '''
        Description: This method matches existing simple pillars with architecture pillars as well as
        simple polygons with architecture pillars.
        Params: simple_polygons: list[Polygon], architecture_pillars: list[Pillar]
        Return: simple_polygons: list[Polygon], architecture_pillars: list[Pillar], log_messages: list[LogMessage]
        '''
        amount_pillars = 0
        for polygon in simple_polygons:
            if polygon.pillars:
                for pillar in polygon.pillars:
                    amount_pillars += 1

        main_logger.info("Matching pillars")
        progress_bar = tqdm(total=amount_pillars)
        progress_bar.set_description("Matching Pillars - Progress:")
        for polygon in simple_polygons:
            if polygon.pillars:
                for simple_pillar in polygon.pillars:
                    progress_bar.update(1)
                    pillar_distances = []
                    potential_pillar = None
                    potential_pillar_distance = 0
                    for architecture_pillar in architecture_pillars:
                        if not architecture_pillar.center_point:
                            continue
                        pillar_distance = ExtractionHelper.get_length_between_points(simple_pillar.start_point, architecture_pillar.center_point)
                        if not potential_pillar:
                            potential_pillar = architecture_pillar
                            potential_pillar_distance = pillar_distance
                        elif pillar_distance < potential_pillar_distance:
                            potential_pillar = architecture_pillar
                            potential_pillar_distance = pillar_distance
                    if potential_pillar_distance < potential_pillar.radius + PILLAR_DISTANCE_THRESHOLD:
                        simple_pillar.pillar_id = potential_pillar.pillar_id
                        simple_pillar.center_point = potential_pillar.center_point
                        simple_pillar.radius = potential_pillar.radius
                        potential_pillar.is_matched = True
                        architecture_pillars = self.match_pillar_by_id(architecture_pillars, potential_pillar.pillar_id)
        progress_bar.close()
        counter = 0
        for pillar in architecture_pillars:
            if pillar.is_matched:
                counter += 1
        main_logger.info("First match amount: {}".format(str(counter)))
        counter = 0
        #2. Durchgang:
        for polygon in simple_polygons:
            for architecture_pillar in architecture_pillars:
                if architecture_pillar.is_matched:
                    continue
                if architecture_pillar.lines:
                    if len(architecture_pillar.points) < 3:
                        continue
                    shapely_poly_pillar = ExtractionHelper.transform_points_to_shapely_polygon(architecture_pillar.points)
                    center_point_pillar = ExtractionHelper.get_point_from_coordinate(list(shapely_poly_pillar.centroid.coords)[0])
                else:
                    center_point_pillar = architecture_pillar.center_point
                shapely_polygon = ExtractionHelper.transform_polygon_to_shapely_polygon(polygon)
                shapely_point = ShapelyPoint(center_point_pillar.x_coordinate, center_point_pillar.y_coordinate)
                if shapely_polygon.contains(shapely_point):
                    if not polygon.pillars:
                        polygon.pillars = []
                    polygon.pillars.append(architecture_pillar)
                    counter = counter + 1
                    architecture_pillar.is_matched = True

        main_logger.info("Second match amount: {}".format(str(counter)))
        counter = 0
        for pillar in architecture_pillars:
            if pillar.is_matched:
                counter += 1

        pillars_flat = []
        for polygon in simple_polygons:
            if polygon.pillars:
                for simple_pillar in polygon.pillars:
                    pillars_flat.append(simple_pillar)
        
        pillar_ids = []
        for pillar in pillars_flat:
            pillar_ids.append(pillar.pillar_id)

        log_messages = []
        log_messages.append(LogMessage("CombinedPlanExtraction", "Amount of matched pillars", str(counter)))
        main_logger.info("Amount of matched pillars: {}".format(str(counter)))
        has_duplicate_items = any(pillar_ids.count(x) > 1 for x in pillar_ids)
        main_logger.info("Duplicate pillar matches: {}".format(str(has_duplicate_items)))
        return simple_polygons, architecture_pillars, log_messages

    def match_pillar_by_id(self, architecture_pillars: list[Pillar], pillar_id: str) -> list[Pillar]:
        '''
        Description: This method finds a architecture pillar by id and sets it to matched
        Params: architecture_pillars: list[Pillar], pillar_id: str
        Return: architecture_pillars: list[Pillar]
        '''
        for pillar in architecture_pillars:
            if pillar.pillar_id == pillar_id:
                pillar.is_matched = True
        return architecture_pillars

    def match_windows(self, polygons: list[Polygon], windows: list[Window]) -> tuple[list[Polygon], list[Window], list[LogMessage]]:
        '''
        Description: This method matches walls of simple polygons with windows.
        Params: polygons: list[Polygon], windows: list[Window]
        Return: polygons: list[Polygon], windows: list[Window], log_messages: list[LogMessage]
        '''
        main_logger.info("Matching windows")

        amount_windows = len(windows)
        progress_bar = tqdm(total=amount_windows)
        progress_bar.set_description("Matching Windows - First Iteration - Progress:")
        for window in windows:
            progress_bar.update(1)
            window.amount_matched = 0
            window.is_matched = False
            #create 2 linestrings
            line_string_start = ExtractionHelper.create_line_string_of_two_points(window.center_point, window.start_point)
            line_string_end = ExtractionHelper.create_line_string_of_two_points(window.center_point, window.end_point)
            #loop through polygons
            for polygon in polygons:
                matched = False
                for wall in polygon.walls:
                    line_string_wall =ExtractionHelper.create_line_string_of_two_points(wall.start_point, wall.end_point)
                    if line_string_wall.intersects(line_string_start) or line_string_wall.intersects(line_string_end):
                        window.is_matched = True
                        matched = True
                        if not wall.windows:
                            wall.windows = []
                        wall.windows.append(window)
                if matched:
                    if not polygon.windows:
                        polygon.windows = []
                    window.amount_matched = window.amount_matched + 1
                    polygon.windows.append(window)
        progress_bar.close()

        amount_walls = 0
        for polygon in polygons:
            for wall in polygon.walls:
                amount_walls += 1
        progress_bar = tqdm(total=amount_walls)
        progress_bar.set_description("Matching Windows - Second Iteration - Progress:")
        for polygon in polygons:
            for wall in polygon.walls:
                progress_bar.update(1)
                line_string_wall =ExtractionHelper.create_line_string_of_two_points(wall.start_point, wall.end_point)
                for window in windows:
                    if window.is_matched:
                        continue 
                    line_string_start = ExtractionHelper.create_line_string_of_two_points(window.center_point, window.start_point)
                    line_string_end = ExtractionHelper.create_line_string_of_two_points(window.center_point, window.end_point)
                    distance_center_start_wall = line_string_start.distance(line_string_wall)
                    distance_center_end_wall = line_string_end.distance(line_string_wall)
                    
                    if distance_center_start_wall <= MAX_WINDOW_DISTANCE or distance_center_end_wall <= MAX_WINDOW_DISTANCE:
                        window.is_matched = True
                        if not wall.windows:
                            wall.windows = []
                        wall.windows.append(window)
                        if not polygon.windows:
                            polygon.windows = []
                            polygon.windows.append(window)
                        else:
                            window_already_in_polygon = False
                            for poly_window in polygon.windows:
                                if window.window_id == poly_window.window_id:
                                    window_already_in_polygon = True
                            if not window_already_in_polygon:
                                polygon.windows.append(window)
        progress_bar.close()
        counter = 0
        for window in windows:
            if not window.is_matched:
                counter = counter + 1
        main_logger.info("Window matching done")
        main_logger.info("Amount of unmatched windows: {}".format(str(counter)))
        main_logger.info("Total amount of windows: {}".format(str(len(windows))))

        log_messages = []
        log_messages.append(LogMessage("CombinedPlanExtraction", "Amount of unmatched windows", str(counter)))
        return polygons, windows, log_messages

    def matching_simple_walls_with_polygons(self, simple_polygons: list, architecture_wall_list: list[Architecture_Wall]) -> tuple[list[Polygon], list[Architecture_Wall]]:
        '''
        Description: This method matches all walls from simple walls with architecture_walls.
        Params: simple_polygons: list, architecture_wall_list: list[Architecture_Wall]
        Return: simple_polygons: list, architecture_wall_list: list[Architecture_Wall]
        Exception: ---
        '''

        line_list_total = []

        for architecture_wall in architecture_wall_list:
            lines = architecture_wall.lines
            for y in lines:
                line_list_total.append(y)

        main_logger.info("Matching architecture walls with simple walls")
        amount_walls = 0
        for polygon in simple_polygons:
            for wall in polygon.walls:
                amount_walls += 1

        progress_bar = tqdm(total=amount_walls)
        progress_bar.set_description("Matching Architecture Walls - Progress:")
        amount_matches = 0
        for simple_polygon in simple_polygons:
            walls = simple_polygon.walls
            for simple_wall in walls:
                progress_bar.update(1)
                simple_line = ExtractionHelper.create_linestring_from_wall(simple_wall)

                for architecture_wall in architecture_wall_list:
                    for line in architecture_wall.lines:

                        if self.is_line_on_line(simple_line, line.line_string):
                            
                            if(simple_wall.wall_thickness == None):
                                simple_wall.wall_thickness = architecture_wall.wall_thickness
                                amount_matches += 1
                            simple_wall.wall_type = architecture_wall.wall_type
                            
                            architecture_wall.simple_wall_ids.append(str(simple_wall.wall_id))
                            
                            break

        progress_bar.close()
        main_logger.info("Amount of matched simple walls: {}".format(str(amount_matches)))
        main_logger.info('Matching Architecture walls done')
        log_messages = []
        log_messages.append(LogMessage("CombinedPlanExtraction", "Amount of matched simple walls", str(amount_matches)))

        return simple_polygons, architecture_wall_list, log_messages

    def is_line_on_line(self, first_line: LineString, second_line: LineString) -> bool:
        '''
        Description: This method checks if two lines are crossing each other or are nearby.
        Params: first_line: LineString, second_line: LineString
        Return: result: bool
        Exception: ---
        '''
        condition_1 = first_line.intersects(second_line)
        condition_2 = first_line.distance(second_line) < INTERSECTING_LINE_THRESHOLD
        return condition_1 or condition_2

    def calculate_window_length(self, polygons: list[Polygon], facade_lines: list[Line], facade_arcs: list[FacadeArc])-> tuple[list[Polygon], list[LogMessage]]:
        '''
        Description: This method calculates the window length of outer walls in simple polygons
        Params: polygons: list[Polygon], facade_lines: list[Line], facade_arcs: list[FacadeArc]
        Return: polygons: list[Polygon], log_messages: list[LogMessage]
        '''
        amount_walls = 0
        for polygon in polygons:
            for wall in polygon.walls:
                if not wall.is_outer_wall:
                    continue
                amount_walls += 1
        counter = 0
        main_logger.info("Calculating window length")
        progress_bar = tqdm(total=amount_walls)
        progress_bar.set_description("Window Length Calculation - Progress:")
        for polygon in polygons:
            for wall in polygon.walls:
                if not wall.is_outer_wall:
                    continue
                progress_bar.update(1)
                window_length = self.get_window_length(wall, facade_lines, facade_arcs)
                wall.window_length = window_length
                if window_length > 0.0:
                    counter += 1
        progress_bar.close()
        main_logger.info("Amount of calculated window lengths: {}".format(str(counter)))
        main_logger.info("Window length calculation done")
        log_messages = []
        log_messages.append(LogMessage("CombinedPlanExtraction", "Amount of calculated window lengths", str(counter)))
        return polygons, log_messages

    def get_window_length(self, wall: Wall, facade_lines: list[Line], facade_arcs: list[FacadeArc]) -> float:
        '''
        Description: This method calculates the window length of a single wall
        Params: wall: Wall, facade_lines: list[Line], facade_arcs: list[FacadeArc]
        Return: window_length: float
        '''
        window_length = self.get_window_length_of_lines(wall, facade_lines)
        window_length_sum = 0.0
        wall_length = ExtractionHelper.get_length_between_points(wall.start_point, wall.end_point)
        if window_length < wall_length:
            for facade_arc in facade_arcs:
                if facade_arc.lines:
                    window_length_new = self.get_window_length_of_lines(wall, facade_arc.lines)
                    window_length_sum += window_length_new
        return min(window_length + window_length_sum, wall_length)

    def get_window_length_of_lines(self, wall: Wall, lines: list[Line])->float:
        '''
        Description: This method calculates the window length of a single wall lines
        Params: wall: Wall, lines: list[Line]
        Return: window_length: float
        '''
        wall_line_string = ExtractionHelper.transform_wall_to_line_string(wall)
        window_length_sum = 0.0
        for line in lines:
            window_length = 0.0
            if not self.is_point_on_line(wall.start_point, line.line_string) and not self.is_point_on_line(wall.end_point, line.line_string):
                if self.is_point_on_line(line.start_point, wall_line_string) and self.is_point_on_line(line.end_point, wall_line_string):
                    window_length = ExtractionHelper.get_length_between_points(line.start_point, line.end_point)
            elif self.is_point_on_line(wall.start_point, line.line_string) and self.is_point_on_line(wall.end_point, line.line_string):
                window_length = ExtractionHelper.get_length_between_points(wall.start_point, wall.end_point)
            else:
                wall_point_on_line = None
                line_point_on_wall = None
                if self.is_point_on_line(wall.start_point, line.line_string):
                    wall_point_on_line = wall.start_point
                elif self.is_point_on_line(wall.end_point, line.line_string):
                    wall_point_on_line = wall.end_point
            
                if self.is_point_on_line(line.start_point, wall_line_string):
                    line_point_on_wall = line.start_point
                elif self.is_point_on_line(line.end_point, wall_line_string):
                    line_point_on_wall = line.end_point
                
                if wall_point_on_line and line_point_on_wall:
                    window_length = ExtractionHelper.get_length_between_points(wall_point_on_line, line_point_on_wall)
            window_length_sum += window_length
        return window_length_sum

    def is_point_on_line(self, point: Point, line: LineString) -> bool:
        '''
        Description: This method checks if a point is on (or near) a line
        Params: point: Point, line: LineString
        Return: is_point_on_line: bool
        '''
        coordinate = ShapelyPoint(point.x_coordinate, point.y_coordinate)
        return line.distance(coordinate) < WINDOW_LENGTH_THRESHOLD
    
    def combine_extracted_functionalities(self, extracted_functionalities_simple: ExtractedFunctionalities, extracted_functionalities_architecture: ExtractedFunctionalities) -> ExtractedFunctionalities:
        '''
        Description: This method is used to combined extraced_functionalities. 
        Params: extracted_functionalities_simple: ExtractedFunctionalities, extracted_functionalities_architecture: ExtractedFunctionalities,  
        Return: extracted_functionalities_for_return: ExtractedFunctionalities
        Exception: ---
        '''
        extracted_functionalities_for_return = ExtractedFunctionalities()

        # Simple Plan Functionalities
        if extracted_functionalities_simple.outer_walls:
            extracted_functionalities_for_return.outer_walls = True
        if extracted_functionalities_simple.match_room:
            extracted_functionalities_for_return.match_room = True
        if extracted_functionalities_simple.area:
            extracted_functionalities_for_return.area = True
        if extracted_functionalities_simple.perimeter:
            extracted_functionalities_for_return.perimeter = True
        if extracted_functionalities_simple.orientation:
            extracted_functionalities_for_return.orientation = True
        if extracted_functionalities_simple.neighbours:
            extracted_functionalities_for_return.neighbours = True

        # Architecture Plan Functionalities
        if extracted_functionalities_architecture.architecture_light_walls:
            extracted_functionalities_for_return.architecture_light_walls = True
        if extracted_functionalities_architecture.architecture_load_bearing_walls:
            extracted_functionalities_for_return.architecture_load_bearing_walls = True
        if extracted_functionalities_architecture.architecture_pillars:
            extracted_functionalities_for_return.architecture_pillars = True
        if extracted_functionalities_architecture.architecture_windows:
            extracted_functionalities_for_return.architecture_windows = True
        if extracted_functionalities_architecture.architecture_facade_arcs:
            extracted_functionalities_for_return.architecture_facade_arcs = True
        if extracted_functionalities_architecture.architecture_facade_lines:
            extracted_functionalities_for_return.architecture_facade_lines = True
    
        return extracted_functionalities_for_return
