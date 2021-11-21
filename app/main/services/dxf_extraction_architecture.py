import math
import statistics
import uuid
from datetime import datetime
from re import X

import ezdxf
import numpy as np
from app.main.constants import *
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.models.architecture_plan import Architecture_Plan
from app.main.models.architecture_wall import Architecture_Wall
from app.main.models.facade_arc import FacadeArc
from app.main.models.line import Line
from app.main.models.pillar import Pillar
from app.main.models.point import Point
from app.main.models.window import Window
from app.main.reporting.reporting_models import (ExtractedFunctionalities,
                                                 LogMessage)
from app.main.services.extraction_helper import ExtractionHelper
from ezdxf.document import Drawing
from ezdxf.entities import Arc
from ezdxf.entities.lwpolyline import LWPolyline
from loguru import logger
from shapely.ctypes_declarations import prototype
from shapely.geometry import LineString
from shapely.geometry import Point as ShapelyPoint
from tqdm import tqdm

main_logger = logger.bind()
class DxfExtractionArchitecture:
    level: int
    def entry_point(self, extraction_request_file: ExtractionRequestFile, dxf_file: Drawing, level: int) -> tuple[Architecture_Plan, ExtractedFunctionalities,  list[LogMessage], list[LineString]]:
        
        # init ExtractedFunctionalities with all values = False (default)
        extracted_functionalities = ExtractedFunctionalities()
        
        '''
        Description: This method is the entry point for every architecture extraction order.
        Params: extraction_request_file: ExtractionRequestFile, dxf_file: Drawing
        Return: architecture_Plan: Architecture_Plan, extracted_functionalities: ExtractedFunctionalities,
        log_messages: LogMessages, linestrings_list_total: list[LineString]
        Exception: ---
        '''
        self.level = level
        start_time = datetime.now()
        log_messages = []
        architecture_walls_tragwand, line_list_total_tragwand = self.extract_architecture_walls(LIGHT_WALL_LAYER, extraction_request_file)
        extracted_functionalities.architecture_light_walls = True 
        architecture_walls_leichtwand, line_list_total_leichtwand = self.extract_architecture_walls(LOAD_BEARING_WALL_LAYER, extraction_request_file)
        extracted_functionalities.architecture_load_bearing_walls = True
        architecture_walls_total = self.get_total_wall_list(architecture_walls_tragwand, architecture_walls_leichtwand)
        
        linestrings_list_total = self.get_total_line_string_list(line_list_total_tragwand, line_list_total_leichtwand)
        #get pillars
        pillars, extracted_functionalities = self.get_pillars(dxf_file, extracted_functionalities)
        #get windows
        windows, extracted_functionalities = self.get_windows(dxf_file, extracted_functionalities)
        #get facade lines
        facade_lines, extracted_functionalities = self.get_facade_lines(dxf_file, extracted_functionalities)
        #get facade arcs
        facade_arcs, extracted_functionalities = self.get_facade_arcs(dxf_file, extracted_functionalities)

        file_path = extraction_request_file.file_path
        file_path = extraction_request_file.file_path
        file_name = extraction_request_file.file_name
        floor_height = extraction_request_file.floor_height
        #get extracted functionalities
        end_time = datetime.now()-start_time
        time_message = "runtime {} seconds".format(str(end_time.seconds))

        log_messages.append(LogMessage("ArchitecturePlanExtraction","File", extraction_request_file.file_name))
        log_messages.append(LogMessage("ArchitecturePlanExtraction", "Count walls", len(architecture_walls_total)))
        log_messages.append(LogMessage("ArchitecturePlanExtraction", "Count pillars", len(pillars)))
        log_messages.append(LogMessage("ArchitecturePlanExtraction", "Count windows", len(windows)))
        log_messages.append(LogMessage("ArchitecturePlanExtraction", "Count facade lines", len(facade_lines)))
        log_messages.append(LogMessage("ArchitecturePlanExtraction", "Count facade_arcs", len(facade_arcs)))
        log_messages.append(LogMessage("ArchitecturePlanExtraction", "Performance", time_message))
        


        return Architecture_Plan(file_name, file_path, floor_height, architecture_walls_total,
            pillars, windows, facade_lines, facade_arcs=facade_arcs), extracted_functionalities, log_messages, linestrings_list_total

    def extract_architecture_walls(self, layer: str,  plan: ExtractionRequestFile) -> tuple[list[Architecture_Wall], list[Line]]:
        '''
        Description: This method is extracts all architecture plan walls.
        Params: layer: str,  plan: ExtractionRequestFile
        Return: architecture_wall_list: list[ArchitectureWall], line_list_total: list[Line]
        Exception: ---
        '''
        #Hilfslisten und variablen
        linestrings_architecture = []
        architecture_wall_list = []
        line_list_total = []
        walltype = ''
        main_logger.info("Extracting architecture walls in layer {}".format(layer))

        architecture_polylines = ExtractionHelper.get_architecture_polylines(plan, layer)
        if(type(architecture_polylines[0]) is ezdxf.entities.lwpolyline.LWPolyline):
            polylines_length = len(architecture_polylines)
            progress_bar = tqdm(total=polylines_length)
            progress_bar.set_description("Architecture Walls layer {} - Progress".format(layer))
            #loop durch alle architecture polylines
            for polyline in architecture_polylines:
                progress_bar.update(1)
                # uuid für die wand erzeugen
                uuid_wall = str(uuid.uuid4())
                # aus jeder architecture_polyline wird eine liste aus linestrings generiert
                linestrings = ExtractionHelper.create_linestring_from_polyline(polyline)
                # jede der linestrings werden in ein object line mit der uuid und einem linestring der Wall zugeorndet
                transformed_linestrings = self.transform_linestrings(linestrings) 
                lines = []
                for x in transformed_linestrings:
                    points = x.coords
                    point_models = []
                    for point in points:
                        prelim = Point(point[0], point[1])
                        point_model = self.transform_point(prelim)
                        #print("LOOP:" + str(point_model))
                        point_models.append(point_model)
                    
                    line = Line(uuid_wall, x, point_models[0], point_models[1])
                    lines.append(line)
                    line_list_total.append(line)
                    linestrings_architecture.append(x)
                
                # wanddicke ermitteln
                wall_thickness = self.calculate_wallthickness(polyline)
                # erzeugen einer Archtiecture_wall
                if(layer == LIGHT_WALL_LAYER):
                    walltype = MATCHED_WALL_TYPES.LIGHT_WALL.name.lower()#'light wall'
                if(layer == LOAD_BEARING_WALL_LAYER):
                    walltype = MATCHED_WALL_TYPES.LOAD_BEARING_WALL.name.lower()#'load-bearing wall'

                architecture_Wall = Architecture_Wall(uuid_wall, polyline, wall_thickness, walltype, lines, [])
                
                # architecture wall in die liste der architecture walls einfügen.
                architecture_wall_list.append(architecture_Wall)
            progress_bar.close()
        return architecture_wall_list, line_list_total

    def transform_linestrings(self, linestrings: list[LineString])-> list[LineString]:
        #TODO
        transformed_linestrings=[]
        for element in linestrings:
            try:
                point1, point2 = element.boundary
                point1 = Point(point1.x, point1.y)
                point2 = Point(point2.x, point2.y)
                point1 = self.transform_point(point1)
                point2 = self.transform_point(point2)
                linestring = ExtractionHelper.create_line_string_of_two_points(point1, point2)
                transformed_linestrings.append(linestring)
            except:
                main_logger.warning("corrupt polyline found")
        return transformed_linestrings

    def get_polylines_by_layer(self, layer: str, entity: str, plan: ExtractionRequestFile) -> tuple[list[LWPolyline], str]:
        '''
        Description: This method gets a ezdxf entity from a specific layer from a plan.
        Params: layer: str, entity: str, plan: ExtractionRequestFile
        Return:  polylines_list: list[LWPolyline], layer: str
        Exception: ---
        '''
        dxf_file = ezdxf.readfile(plan.file_path + plan.file_name)
        md = dxf_file.modelspace()
        query_string = f"{entity}[layer=='{layer}']"
        polylines = md.query(query_string)
        polylines_list = []
        for x in polylines:
            polylines_list.append(x)
        return polylines_list, layer

    def get_total_wall_list(self, architecture_walls_tragwand: list, architecture_walls_leichtwand: list) -> list[Architecture_Wall]:
        '''
        Description: This method creates a total list of architecture walls.
        Params: architecture_walls_tragwand: list, architecture_walls_leichtwand: list
        Return:  architecture_walls_total: list[Archtecture_wall]
        Exception: ---
        '''
        architecture_walls_total =[]
        for x in architecture_walls_tragwand:
            architecture_walls_total.append(x)
        for x in architecture_walls_leichtwand:
            architecture_walls_total.append(x)
        return architecture_walls_total

    def get_total_line_string_list(self, linestrings_tragwand: list, linestrings_leichtwand: list) -> list[LineString]:
        '''
        Description: This method creates a total list of linestrings.
        Params: linestrings_tragwand: list, linestrings_leichtwand: list
        Return:  linestrings_list_total: list[Linestring]
        Exception: ---
        '''
        linestrings_list_total =[]
        for x in linestrings_tragwand:
            linestrings_list_total.append(x)
        for x in linestrings_leichtwand:
            linestrings_list_total.append(x)
        return linestrings_list_total

    def calculate_wallthickness(self, polyline: LWPolyline) -> float:
        '''
        Description: This method indicates and calculates from one polyline a wallthickness.
        Params: polyline: LWPolyline
        Return:  linestring_list: list[Linestring]
        Exception: ---
        '''
        wallthickness = 0.0
        
        linestring_list = ExtractionHelper.create_linestring_from_polyline(polyline)
        list_avg = []
        for x in linestring_list:
            if(x.length < SMALL_WALL_LINE_THRESHOLD):
                list_avg.append(x.length)
        if(len(list_avg) < 1):
            wallthickness = DEFAULT_WALL_THICKNESS
            return wallthickness        
        else:
            wallthickness = statistics.mean(list_avg)
            return wallthickness


    def get_pillars(self, dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities) -> tuple[list[Pillar], ExtractedFunctionalities]:
        '''
        Description: This method extracts all pillars (circles and polygons) from an architecture plan.
        Params: dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities
        Returns: pillars: list[Pillar], extracted_functionalities: ExtractedFunctionalities
        '''
        
        main_logger.info("Extracting architecture pillars")
        architecture_model = dxf_file.modelspace()
        pillars_dxf = architecture_model.query("CIRCLE[layer=='{}']".format(PILLAR_LAYER))
        pillar_polylines_dxf = architecture_model.query("LWPolyline[layer=='{}']".format(PILLAR_LAYER))
        pillars_length = len(pillars_dxf) + len(pillar_polylines_dxf)
        progress_bar = tqdm(total=pillars_length)
        progress_bar.set_description("Architecture Pillars - Progress")
        pillars = []
        for pillar_dxf in pillars_dxf:
            progress_bar.update(1)
            pillar = self.create_architecture_pillar(pillar_dxf.dxf.center, pillar_dxf.dxf.radius)
            pillars.append(pillar)

        for polyline in pillar_polylines_dxf:
            progress_bar.update(1)
            coordinates = polyline.get_points("XY")
            pillar = self.create_architecture_pillar_with_lines(coordinates)
            points = []
            for coordinate in coordinates:
                point = ExtractionHelper.get_point_from_coordinate(coordinate)
                point = self.transform_point(point)
                points.append(point)
            pillar.points = points
            pillars.append(pillar)
        progress_bar.close()

        extracted_functionalities.architecture_pillars = True
        
        return pillars, extracted_functionalities

    def create_architecture_pillar_with_lines(self, coordinates: list[tuple]) -> Pillar:
        '''
        Description: This method creates an architecture pillar with lines from coordinates.
        Params: coordinates: list[tuple]
        Return: pillar: Pillar
        '''
        lines = []
        for i in range(len(coordinates) - 1):
            start_point = ExtractionHelper.get_point_from_coordinate(coordinates[i])
            start_point = self.transform_point(start_point)
            end_point = ExtractionHelper.get_point_from_coordinate(coordinates[i+1])
            end_point = self.transform_point(end_point)
            line = Line(start_point=start_point, end_point=end_point)
            lines.append(line)
        pillar_id = str(uuid.uuid4())
        return Pillar(lines=lines, pillar_id=pillar_id)

    def create_architecture_pillar(self, center: tuple, radius: float) -> Pillar:
        '''
        Description: This method creates an architecture pillar from a center point and  a radius.
        Params: center: tuple, radius: float
        Return: pillar: Pillar
        '''
        center_point = Point(center[0], center[1])
        center_point = self.transform_point(center_point)
        pillar_id = str(uuid.uuid4())
        return Pillar(center_point=center_point, radius=radius, pillar_id=pillar_id)


    def get_windows(self, dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities) -> tuple[list[Window], ExtractedFunctionalities]:
        '''
        Description: This method extracts all windows from an architecture plan.
        Params: dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities
        Return: windows: list[Window], extracted_functionalities: ExtractedFunctionalities
        '''
        main_logger.info("Extracting architecture windows")
        architecture_model = dxf_file.modelspace()
        facade_arcs = architecture_model.query("ARC[layer=='{}']".format(FACADE_LAYER))
        counter = 0
        for facade_arc in facade_arcs:
            if facade_arc.dxf.radius <= MAX_WINDOW_RADIUS:
                counter += 1
        progress_bar = tqdm(total=counter)
        progress_bar.set_description("Architecture Windows - Progress")
        windows = []
        for facade_arc in facade_arcs:
            if facade_arc.dxf.radius <= MAX_WINDOW_RADIUS:
                progress_bar.update(1)
                window = self.create_architecture_window(facade_arc)
                windows.append(window)
        progress_bar.close()

        extracted_functionalities.architecture_windows = True

        return windows, extracted_functionalities

    def create_architecture_window(self, arc: Arc) -> Window:
        '''
        Description: This method creates an architecture window from a given ezdxf arc
        Params: arc: Arc
        Return: window: Window
        '''
        window_id = str(uuid.uuid4())
        angle = abs(arc.dxf.start_angle - arc.dxf.end_angle)
        center_point = ExtractionHelper.get_point_from_coordinate(arc.dxf.center)
        center_point = self.transform_point(center_point)
        start_point = ExtractionHelper.get_point_from_coordinate(arc.start_point)
        start_point = self.transform_point(start_point)
        end_point = ExtractionHelper.get_point_from_coordinate(arc.end_point)
        end_point = self.transform_point(end_point)
        radius = arc.dxf.radius
        return Window(window_id, center_point, start_point, end_point, radius, angle)

    def get_facade_arcs(self, dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities) -> tuple[list[FacadeArc], ExtractedFunctionalities]:
        '''
        Description: This method extracts all facade arcs of an architecture plan and transforms it to lines.
        Params: dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities
        Return: facade_arcs: list[FacadeArc], extracted_functionalities: ExtractedFunctionalities
        '''
        main_logger.info("Extracting facade arcs")
        architecture_model = dxf_file.modelspace()
        dxf_arcs = architecture_model.query("ARC[layer=='{}']".format(FACADE_LAYER))
        facade_arcs = []
        for dxf_arc in dxf_arcs:
            if dxf_arc.dxf.radius > MAX_WINDOW_RADIUS:
                facade_arcs.append(self.convert_dxf_to_object_arc(dxf_arc))
        
        extracted_functionalities.architecture_facade_arcs = True

        return facade_arcs, extracted_functionalities

    def get_facade_lines(self, dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities)-> tuple[list[Line], ExtractedFunctionalities]:
        '''
        Description: This method extracts all facade lines of an architecture plan.
        Params: dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities
        Return: facade_lines: list[Lines], extracted_functionalities: ExtractedFunctionalities
        '''
        main_logger.info("Extracting facade lines")
        architecture_model = dxf_file.modelspace()
        facade_polylines = architecture_model.query("LWPolyline[layer=='{}']".format(FACADE_LAYER))
        lines_dxf = architecture_model.query("LINE[layer=='{}']".format(FACADE_LAYER))
        lines = ExtractionHelper.create_lines_from_polylines(facade_polylines)
        for line_dxf in lines_dxf:
            line = ExtractionHelper.get_line_from_coordinates(line_dxf.dxf.start, line_dxf.dxf.end)
            lines.append(line)
        
        lines = self.transform_lines(lines)
        extracted_functionalities.architecture_facade_lines = True
        return lines, extracted_functionalities

    def transform_lines(self, lines: list[Line]) -> list[Line]:
        '''
        Description: This method transforms lines to take the offset into account
        Params: lines: list[Line]
        Return: lines: list[Line]
        '''
        for line in lines:
            start_point = self.transform_point(line.start_point)
            end_point = self.transform_point(line.end_point)
            line.start_point = start_point
            line.end_point = end_point
        return lines


    def convert_dxf_to_object_arc(self, dxf_arc: Arc) -> FacadeArc:
        '''
        Description: This method transforms a given dxf arc into a facade arc.
        Params: dxf_arc: Arc
        Return: FacadeArc
        '''
        center_point = ExtractionHelper.get_point_from_coordinate(dxf_arc.dxf.center)
        start_point = ExtractionHelper.get_point_from_coordinate(dxf_arc.start_point)
        end_point = ExtractionHelper.get_point_from_coordinate(dxf_arc.end_point)

        center_point = self.transform_point(center_point)
        start_point = self.transform_point(start_point)
        end_point = self.transform_point(end_point)

        radius = dxf_arc.dxf.radius
        start_angle = dxf_arc.dxf.start_angle
        end_angle = dxf_arc.dxf.end_angle

        perimeter = 2 * math.pi * radius * ((end_angle - start_angle) / 360)
        delta_angle = self.get_delta_angle(perimeter, start_angle, end_angle)
        lines = self.get_arc_lines(start_angle, end_angle, delta_angle, center_point, start_point, end_point, radius)

        return FacadeArc(center_point, start_point, end_point, radius, start_angle, end_angle, perimeter=perimeter, delta_angle=delta_angle, lines=lines)

    def get_delta_angle(self, perimeter: float, start_angle: float, end_angle: float) -> float:
        '''
        Description: This method calculates the delta angle of an arc.
        Params: perimeter: float, start_angle: float, end_angle: float
        Return: delta_angle: float
        '''
        line_length = self.get_arc_line_length(perimeter)
        amount_lines = perimeter / line_length
        return (end_angle - start_angle) / amount_lines

    def get_arc_line_length(self, perimeter: float) -> float:
        '''
        Description: This method calculates the length of one line within the facade arc.
        Params: perimeter: float
        Return: line_length: float
        '''
        if perimeter <= FACADE_ARC_MIN_LINE_LENGTH:
            return perimeter
        ratio = perimeter / FACADE_ARC_MIN_LINE_LENGTH
        amount_lines = math.floor(ratio)
        return perimeter / amount_lines

    def get_arc_lines(self, start_angle: float, end_angle: float, delta_angle: float, center_point: Point, start_point: Point, end_point: Point, radius: float) -> list[Line]:
        '''
        Description: This method calculates all arc lines of a given arc.
        Params: start_angle: float, end_angle: float, delta_angle: float, center_point: Point, start_point: Point, end_point: Point, radius: float
        Return: lines: list[Line]
        '''
        first_point = end_point
        first_angle = end_angle
        line_count = int((end_angle - start_angle) / delta_angle)
        lines = []
        for i in range(line_count):
            second_angle = first_angle - (i + 1) * delta_angle
            second_point = self.get_arc_point(center_point, radius, second_angle)
            line = ExtractionHelper.create_line_from_two_points(first_point, second_point)
            lines.append(line)
            first_point = second_point
        return lines

    def get_arc_point(self, center_point: Point, radius: float, angle: float) -> Point:
        '''
        Description: This method calculates the coordinates of an arc point.
        Params: center_point: Point, radius: float, angle: float
        Return: point: Point
        '''
        dx = radius * np.cos(np.deg2rad(angle))
        dy = radius * np.sin(np.deg2rad(angle))

        x_coordinate = center_point.x_coordinate + dx
        y_coordinate = center_point.y_coordinate + dy

        point = Point(x_coordinate, y_coordinate)

        return point

    def transform_point(self, point: Point) -> Point:
        '''
        Description: This method transforms the points by the given offset in the constants.py.
        Params: center_point: Point, radius: float, angle: float
        Return: point: Point
        '''
        if ENABLE_CUSTOM_OFFSET:
            x = point.x_coordinate + CUSTOM_X_OFFSET
            y = point.y_coordinate + CUSTOM_Y_OFFSET
        elif self.level == 1:
            x = point.x_coordinate + FIRST_LEVEL_X_OFFSET
            y = point.y_coordinate + FIRST_LEVEL_Y_OFFSET
        elif self.level == 2:
            x = point.x_coordinate + SECOND_LEVEL_X_OFFSET
            y = point.y_coordinate + SECOND_LEVEL_Y_OFFSET
        else:
            x = point.x_coordinate
            y = point.y_coordinate
            
        s_width = point.s_width
        e_width = point.e_width
        b_value = point.b_value
        new_point = Point(x, y, s_width=s_width, e_width=e_width, b_value=b_value)
        return new_point
