import math
import uuid

import ezdxf
import numpy as np
from app.main.constants import *
from app.main.dtos.request.extraction_request_file import ExtractionRequestFile
from app.main.models.polygon import Polygon
from app.main.models.simple_plan import Simple_Plan
from app.main.reporting.reporting_models import (ExtractedFunctionalities,
                                                 LogMessage)
from app.main.reporting.reporting_service import ReportingService
from app.main.services.extraction_helper import ExtractionHelper
from app.main.services.neighbour_extraction import NeighbourExtraction
from app.main.services.orientation_extraction import OrientationExtraction
from app.main.services.outer_wall_extraction import OuterWallExtraction
from app.main.services.room_extraction import RoomExtraction
from app.main.services.room_geometry import RoomGeometry
from app.main.services.walls_extraction import WallsExtraction
from ezdxf.document import Drawing
from ezdxf.entities.lwpolyline import LWPolyline
from loguru import logger
from shapely.geometry import LineString, Point
from shapely.geometry import Polygon as ShapelyPolygon
from tqdm import tqdm

'''
Description: This class contains the main extraction logic to retrieve data from a simple plan.
'''

main_logger = logger.bind()

class DxfExtractionSimple:
    def entry_point(self, extraction_request_file: ExtractionRequestFile, dxf_file: Drawing) -> tuple[Simple_Plan, ExtractedFunctionalities, list[LogMessage]]:
        '''
        Desciption: This method is the main entry point of the extraction of simple plans.
        Params: extraction_request_file: ExtractionRequestFile, dxf_file: Drawing
        Return: simple_plan_for_return: Simple_Plan, extracted_functionalities: ExtractedFunctionalities, log_messages: list[LogMessage]
        '''

        if not isinstance(extraction_request_file, ExtractionRequestFile):
            main_logger.critical("unable to start DxfExtractionSimple because param : {} is not an instance of ExtractionRequestFile".format(
                type(extraction_request_file)))
        if not isinstance(dxf_file, Drawing):
            main_logger.critical(
                "unable to start DxfExtractionSimple because param : {} is not an instance of Drawing".format(type(dxf_file)))

        log_messages = []
        start_simple_plan_extraction_time = datetime.now()
        
        extracted_functionalities = ExtractedFunctionalities()
        
        file_path = extraction_request_file.file_path
        file_name = extraction_request_file.file_name
        floor_height = extraction_request_file.floor_height
        orientation = extraction_request_file.orientation

        simple_plan_for_return = Simple_Plan(
            file_path=file_path, file_name=file_name, floor_height=floor_height, orientation=orientation)

        polygons, polygons_with_virtual_entities, extracted_functionalities, counter_polygon_closed = self.get_all_polygons(
            dxf_file, file_path + file_name, orientation=orientation, log_message=log_messages)

        roomExtraction = RoomExtraction()
        polygons, unmatched_room_stamps, extracted_functionalities = roomExtraction.match_polygons_with_rooms(
            polygons, polygons_with_virtual_entities, dxf_file, extracted_functionalities)


        simple_plan_for_return.polygons = polygons
        simple_plan_for_return.unmatched_rooms = unmatched_room_stamps

        log_messages.append(LogMessage("SimplePlanExtraction","File", file_name))
        log_messages.append(LogMessage("SimplePlanExtraction","count polygons", len(simple_plan_for_return.polygons)))
        log_messages.append(LogMessage("SimplePlanExtraction","GenerateWalls", " Polygons closed : {} ".format(counter_polygon_closed)))
        end_simple_plan_extraction_time = datetime.now()-start_simple_plan_extraction_time
        message = ('runtime: %s seconds' % (end_simple_plan_extraction_time.seconds))
        log_messages.append(LogMessage("SimplePlanExtraction","Performance", message))
                
        return simple_plan_for_return, extracted_functionalities, log_messages

    def get_all_polygons(self, dxf_file: Drawing, file_path: str, orientation = None, log_message: LogMessage = None) -> tuple[
        list[Polygon], list[dict], ExtractedFunctionalities, int]:
        '''
        Description: This method contains the main logic for the extraction of the simple plan.
            Here, all polygons and their attributes are extracted.
        Params: dxf_file: Drawing, file_path: str, orientation, log_message: LogMessage
        Return: polygons: list[Polygon], polygons_with_virtual_entities: list[dict], 
            extracted_functionalities: ExtractedFunctionalities, counter_polygon_closed: int
        '''
        yaxis = None

        extracted_functionalities = ExtractedFunctionalities(
            area=True, perimeter=True)
        
        if COMPASS_ORIENTATION_PRIORITIZED:
            try:
                yaxis = OrientationExtraction.get_north_orientation(file_path)[2]
                calculate_orientation = True
                main_logger.info("Orientation will be calculated with compass.")
            except Exception:
                pass

                try:
                    yaxis = OrientationExtraction.get_north_orientation_by_angle(orientation)
                    calculate_orientation = True
                    main_logger.info("Orientation will be calculated with angle.")
                except KeyError:
                    calculate_orientation = False
                    main_logger.info("Orientation will NOT be calculated.")
            
        else:
            try:
                yaxis = OrientationExtraction.get_north_orientation_by_angle(orientation)
                calculate_orientation = True
                main_logger.info("Orientation will be calculated with angle.")
            except Exception:
                pass
    
                try:
                    yaxis = OrientationExtraction.get_north_orientation(file_path)[2]
                    calculate_orientation = True
                    main_logger.info("Orientation will be calculated with compass")
                except KeyError:
                    calculate_orientation = False
                    main_logger.info("Orientation will NOT be calculated.")
        polygons = []
        polygons_with_virtual_entities = []
        dxf_modelspace = ExtractionHelper.get_modelspace(dxf_file)
        outline_polygon = ExtractionHelper.get_outline_polygon(dxf_modelspace)
        
        if IDENTIFY_LOOPS_IN_OUTLINE_POLYGON:
            outline_polygon = ExtractionHelper.remove_loops_from_outline_polygon(outline_polygon, IDENTIFY_LOOPS_IN_OUTLINE_POLYGON_RANGE)


        layer = NUDATA_LAYER_RAUMPOLYGON
        room_polylines = dxf_modelspace.query(
            'LWPolyline[layer=="{}"]'.format(layer))
        main_logger.debug("got all room_polylines on layer: {}".format(layer))
        counter_polygon_closed = 0
        for polyline in room_polylines:
            walls, ignored_edges_length, pillars, polygon_closed = WallsExtraction.create_walls_from_polyline(polyline, log_message)
            if polygon_closed:
                counter_polygon_closed += 1
            coordinates = polyline.get_points("XY")
            coordinates_seb = polyline.get_points('XYSEB')
            if len(coordinates) > 2:
                points = []
                for coordinate in coordinates_seb:
                    point = ExtractionHelper.get_point_from_seb_coordinate(
                        coordinate)
                    points.append(point)
                area, perimeter = ExtractionHelper.get_area_and_perimeter_from_polyline(
                    polyline)
                polygon_id = str(uuid.uuid4())
                polygon = Polygon(polygon_id, area, perimeter, True)
                polygon.walls = walls
                polygon.pillars = pillars
                polygon.points = points
                polygon.ignored_edges_length = ignored_edges_length
                room_geometry = RoomGeometry()
                polygon.amount_corners = room_geometry.get_polygon_corners(polygon)
                polygon.geometry = room_geometry.get_room_geometry(polygon, coordinate, coordinates_seb)
                polygons.append(polygon)
                polygon_with_virtual_entities = self.get_polygon_with_virtual_entities(
                    polyline, polygon_id)
                polygons_with_virtual_entities.append(
                    polygon_with_virtual_entities)


        polygons_length = len(polygons)
        if ENABLE_NEIGHBOURS:
            extracted_functionalities.neighbours = True
            main_logger.info("Extracting neighbours...")
            progress_bar = tqdm(total=polygons_length)
            progress_bar.set_description("Neighbours - Progress")
            neighbour_extraction = NeighbourExtraction()
            for polygon in polygons:
                progress_bar.update(1)
                polygon.adjacent_polygons =  neighbour_extraction.get_neighbours(polygons, polygon)
            progress_bar.close()
            main_logger.info("Neighbours extracted")

        if ENABLE_OUTER_WALLS:
            extracted_functionalities.outer_walls = True
            extracted_functionalities.orientation = calculate_orientation
            main_logger.info(
                'Extracting outer walls...')
            progress_bar = tqdm(total=polygons_length)
            progress_bar.set_description("Outer Walls - Progress")
            for polygon in polygons:
                progress_bar.update(1)
                outer_walls_extraction = OuterWallExtraction()
                polygon = outer_walls_extraction.get_outer_walls(
                    polygons, polygon, yaxis, outline_polygon, calculate_orientation)
            progress_bar.close()
            main_logger.info(
                'Outer walls extracted')

        extracted_functionalities.area = True
        extracted_functionalities.perimeter = True
        return polygons, polygons_with_virtual_entities, extracted_functionalities, counter_polygon_closed

    def get_polygon_with_virtual_entities(self, polyline: LWPolyline, polygon_id: str) -> dict:
        '''
        Description: This method creates a polygon includung virtual entities for matching with a roomstamp.
        Inspiration by: Prototype C
        Params: polyline: LWPolyline, polygon_id: str
        Return: result: dict
        '''
        virtual_entities = self.get_virtual_entities(polygon=polyline)
        polygon = ShapelyPolygon(polyline.get_points('XY'))
        result = {'polygon': polygon, 'all_line_list': virtual_entities['all_line_list'],
                  'straight_line_list_with_length': virtual_entities['straight_line_list_with_length'],
                  'arc_list_with_length': virtual_entities['arc_list_with_length'],
                  'polygon_id': polygon_id
                  }
        return result

    def get_virtual_entities(self, polygon: LWPolyline):
        '''
        Description: Method to get virtual entities (Lines and Arcs) of a polygon (Entity LWPolyline)
        Params: polyline: LWPolyline
        Return: result: dict
        '''
        all_line_list = []
        straight_line_list_with_length = []
        arc_list_with_length = []
        if polygon.dxftype() == 'LWPOLYLINE':
            for e in polygon.virtual_entities():
                if e.dxftype() == 'LINE':
                    start_coords = (e.dxf.start[0], e.dxf.start[1])
                    end_coords = (e.dxf.end[0], e.dxf.end[1])
                    line = LineString([start_coords, end_coords])
                    all_line_list.append({'line': line, 'length': line.length})
                    straight_line_list_with_length.append(
                        {'line': line, 'length': line.length})
                elif e.dxftype() == 'ARC':
                    center_x, center_y = e.dxf.center[0], e.dxf.center[1]
                    radius = e.dxf.radius
                    start_angle, end_angle = e.dxf.start_angle, e.dxf.end_angle
                    if start_angle < 0:
                        start_angle = 360.0 + start_angle
                    if end_angle < 0:
                        end_angle = 360.0 + end_angle
                    num_segments = 100
                    if start_angle < end_angle:
                        angles = np.linspace(
                            start_angle, end_angle, num_segments)
                        start_angle_interval_end = 360.0
                    else:
                        start_angle_interval_end = 360.0
                        end_angle_interval_start = 0.0
                        angles = np.linspace(start_angle, start_angle_interval_end, num_segments) + np.linspace(
                            end_angle_interval_start, end_angle, num_segments)
                    theta = np.radians(angles)
                    x = center_x + radius * np.cos(theta)
                    y = center_y + radius * np.sin(theta)
                    arc_points = np.column_stack([x, y])
                    line = LineString(arc_points)
                    if start_angle < end_angle:
                        angle_sum = end_angle - start_angle
                    else:
                        angle_sum = start_angle_interval_end - start_angle + end_angle
                    arc = (angle_sum / 360) * 2 * math.pi * radius

                    all_line_list.append({'line': line, 'length': arc})
                    arc_list_with_length.append({'arc': line, 'length': arc})

            result = {'all_line_list': all_line_list, 'straight_line_list_with_length': straight_line_list_with_length,
                      'arc_list_with_length': arc_list_with_length}
        else:
            main_logger.warning(
                'Parameter is not a LWPolyline object at getting its virtual entities (Lines and Arcs)')
            result = None
        return result
