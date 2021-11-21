from app.main.reporting.reporting_models import ExtractedFunctionalities
import ezdxf
from app.main.constants import *
from app.main.models.point import Point
from app.main.models.polygon import Polygon
from app.main.models.room import Room
from app.main.services.boundary_lines_extraction import BoundaryLinesExtraction
from app.main.services.extraction_helper import ExtractionHelper
from app.main.services.validation_helper import ValidationHelper
from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
from loguru import logger
from shapely.geometry import LineString
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon

'''
Description: This class contains the extraction logic for retrieving and matching a roomstamp to a polygon and is mainly integrated from prototype c
'''

main_logger = logger.bind()

class RoomExtraction():
    def match_polygons_with_rooms(self, polygons: list[Polygon], polygons_with_virtual_entities: list[Polygon], dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities) -> tuple[list[Polygon], list]:
        '''
        Description: This method coordinates the matching of polygons and rooms.
        Params: polygons: list[Polygon], polygons_with_virtual_entities: list[Polygon], dxf_file: Drawing, extracted_functionalities: ExtractedFunctionalities
        Return: polygons: list[Polygon], unmatched_room_stamps: list
        '''

        model = dxf_file.modelspace()
        annotations = ExtractionHelper.get_all_annotations(
            model=model, layer=NUDATA_LAYER_RAUMSTEMPEL)
        lines_to_annotations = self.get_lines_for_annotations(
            model=model, layer=NUDATA_LAYER_RAUMSTEMPEL)
        matched_object, unmatched_room_stamps = self.match_room_polygons_and_annotations(
            annotations, lines_to_annotations, polygons_with_virtual_entities)
        rooms = []
        for room_obj in matched_object:
            room = self.create_room_from_room_object(room_obj)
            rooms.append(room)

        for polygon in polygons:
            polygon.room = self.get_room_for_polygon_id(rooms, polygon.id)
            if polygon.room == None:
                polygon.has_roomstamp = False
            else:
                polygon.has_roomstamp = True

        extracted_functionalities.match_room = True
        
        return polygons, unmatched_room_stamps, extracted_functionalities

    def create_room_from_room_object(self, room_object: dict):
        '''
        Description: This method transforms the room dictionary to an object of the model structure.
        Params: room_object: dict
        Return: room: Room
        '''
        room_area = room_object['area_annotation']
        room_perimeter = room_object['perimeter_original']
        room_number = room_object['room_number']
        room_type = room_object['room_label']
        polygon_id = room_object['polygon_id']
        room = Room(room_area, room_perimeter, room_number, room_type, polygon_id)
        return room

    def get_room_for_polygon_id(self, rooms: list[dict], polygon_id: str) -> dict:
        '''
        Description: This method retrieves a room dict for a given polygon.
        Params: rooms: list[dict], polygon_id: str
        Return: room_object: dict
        '''
        room = [r for r in rooms if r.polygon_id == polygon_id]
        if len(room) < 1:
            main_logger.warning("no room found for polygon_id {}".format(polygon_id))
            return None
        elif len(room) > 1:
            main_logger.warning("multiple rooms found for polygon_id {}! Taking the first room.".format(polygon_id))
        return room[0]


    def get_lines_for_annotations(self, model: Modelspace, layer: str) -> list[dict]:
        '''
        Description: Method to get all lines/polygons with 2 points (Layer Raumstempel)
        Params: model: Modelspace, layer: str
        Return: result: list[dict]
        '''
        result = []
        if not isinstance(model, Modelspace):
            main_logger.error('unable to get_lines_for_annotations for layer: {} because parameter: {} is not a modelspace object'.format(str(layer), type(model)))

            result = None
        else:
            lines = model.query('LINE[layer=="{}"]'.format(layer))
            for line in lines:
                result.append({'start_location': (line.dxf.start[0], line.dxf.start[1]), 'end_location': (
                    line.dxf.end[0], line.dxf.end[1])})
            polylines = model.query('LWPolyline[layer=="{}"]'.format(layer))
            for polyline in polylines:
                line_points = polyline.get_points('XY')
                if len(line_points) == 2: 
                    result.append(
                        {'start_location': line_points[0], 'end_location': line_points[1]})
        return result

    def match_room_polygons_and_annotations(self, annotations: list, lines_to_annotations: list,
                                            polygons_with_virtual_entities: list) -> tuple[list[dict], list[dict]]:
        '''
        Description: Method to match room polygons and annotations in three steps
        Params: annotations: list, lines_to_annotations: list, polygons_with_virtual_entities: list
        Return: result: list[dict], unmatched_room_stamps: list[dict]
        '''
        result = []
        # check type of parameters
        if type(annotations) != list or type(lines_to_annotations) != list or type(polygons_with_virtual_entities) != list:
            main_logger.warning(
                'Not all parameters are lists at matching room polygons and annotations in three steps')
            return None
        else:
            # match with area check
            for matched in self.match_room_polygons_and_annotations_standard(
                    annotations=annotations, polygons_with_virtual_entities=polygons_with_virtual_entities,
                    area_check=True):
                result.append(matched)  # returns list of room_dict
            main_logger.info('1. step: match_room_polyongs_and_annotations. matched: {}'.format(len(result)))
            # get unmatched annotations
            open_annotations = self.get_unmatched_annotations(annotations=annotations,
                                                              matched_room_polygons_and_annotations=result)
            unmatched_rooms = self.get_unmatched_polygons_with_virtual_entities(
                polygons_with_virtual_entities=polygons_with_virtual_entities,
                matched_room_polygons_and_annotations=result)
            # match open annotations with rooms via line
            matched_list = self.matching_via_line(open_annotations=open_annotations, lines_to_annotations=lines_to_annotations,
                                                  polygons_with_virtual_entities=unmatched_rooms)

            if matched_list:
                for matched in matched_list:
                    result.append(matched)  # returns list of room_dict
            main_logger.info('2. step: match_room_polyongs_and_annotations. matched: {}'.format(len(result)))
            # get remaining unmatched annotations and rooms
            open_annotations = self.get_unmatched_annotations(annotations=annotations,
                                                              matched_room_polygons_and_annotations=result)
            unmatched_rooms = self.get_unmatched_polygons_with_virtual_entities(
                polygons_with_virtual_entities=polygons_with_virtual_entities,
                matched_room_polygons_and_annotations=result)
            # match open annotations without area check
            for matched in self.match_room_polygons_and_annotations_standard(
                    annotations=open_annotations, polygons_with_virtual_entities=unmatched_rooms, area_check=False):
                result.append(matched)  # returns list of room_dict
            main_logger.info('3. step: match_room_polyongs_and_annotations. matched: {}'.format(len(result)))
           
            unmatched_room_stamps = self.get_unmatched_annotations(annotations=annotations,
                                                              matched_room_polygons_and_annotations=result)
            
            return result, unmatched_room_stamps

    def match_room_polygons_and_annotations_standard(self, annotations: list, polygons_with_virtual_entities: list,
                                                     area_check: bool) -> list[dict]:
        '''
        Description: Method to match room polygons and annotations (standard way) with/without area check
        Params: annotations: list, polygons_with_virtual_entities: list, area_check: bool
        Return: result: list[dict]
        '''
        result = []
        if type(annotations) != list or type(polygons_with_virtual_entities) != list:
            main_logger.warning('unable to match_room_polygons_and_annotations_standard because param: {} and/or {} is != list'.format(type(annotations), type(polygons_with_virtual_entities)))
            return None
        elif type(area_check) != bool:
            main_logger.info('Determine if area check should be excecuted at matching room polygons and annotations in standard way')
            return None
        for annotation in annotations:
            for polygon_ext in polygons_with_virtual_entities:
                room = polygon_ext['polygon']
                x_coordinate = annotation[0][2]
                y_coordinate = annotation[0][3]
                if ShapelyPoint(x_coordinate, y_coordinate).within(room):
                    room_obj = self.create_room_object(polygon_ext=polygon_ext, annotation=annotation,
                                                       area_check_standard=area_check, check_line_matching=False,
                                                       manual_matching=False)
                    if room_obj is not None:
                        result.append(room_obj)
                        polygons_with_virtual_entities.remove(polygon_ext)
                    break 
        return result

    def create_room_object(self, polygon_ext, annotation, area_check_standard: bool, check_line_matching: bool,
                           manual_matching: bool) -> dict:
        '''
        Description: Method to create room object (dict)
        Params: polygon_ext, annotation, area_check_standard: bool, check_line_matching: bool, manual_matching: bool
        Return: room_obj: dict
        '''
        if type(area_check_standard) != bool:
            main_logger.info('Determine if area check standard should be excecuted at creating room object of polygon and annotations')
            return None
        elif type(check_line_matching) != bool:
            main_logger.info(
                'Determine if matched by line at creating room object of polygon and annotations')
            return None
        elif type(manual_matching) != bool:
            main_logger.info(
                'Determine if manual matched at creating room object of polygon and annotations')
            return None
        elif type(polygon_ext) != dict:
            main_logger.warning('unable to create_room_object because param : {} has to be a dict'.format(type(polygon_ext)))
            return None
        elif list(polygon_ext.keys()) != ['polygon', 'all_line_list', 'straight_line_list_with_length',
                                          'arc_list_with_length', 'polygon_id']:
            main_logger.warning('unable to create_room_object because polygon dict has to have following keys: polygon, all_line_list, straight_line_list_with_length, '
                  'arc_list_with_length at creating room object of polygon and annotations. got: {}'.format(list(polygon_ext.keys())))
            return None
        elif type(annotation) != list:
            main_logger.warning('unable to create_room_object because param : {} has to be a list'.format(type(annotation)))
            return None
        else:
            room = polygon_ext['polygon']
            room_coords = list(room.exterior.coords)
            room_polygon = ShapelyPolygon(room_coords)
            line_coords_and_lengths_of_polygon = self.get_line_coords_and_length_of_polygon_with_virtual_entities(
                polygon_ext)
            boundary_lines = []
            if not len(line_coords_and_lengths_of_polygon['straight_lines']) + len(
                    line_coords_and_lengths_of_polygon['arc_lines']) == 5:
                if not len(line_coords_and_lengths_of_polygon['straight_lines']) + len(
                        line_coords_and_lengths_of_polygon['arc_lines']) == 3:
                    if line_coords_and_lengths_of_polygon['arc_lines'] or ExtractionHelper.has_inner_points(room_coords, room_polygon):
                        adjusted_polygon_lines = BoundaryLinesExtraction.get_boundary_lines(line_coords_and_lengths_of_polygon['straight_lines'],
                                                                                            line_coords_and_lengths_of_polygon[
                                                                                                'arc_lines'],
                                                                                            annotation[0][1])
                        adjusted_room_coords = ValidationHelper.get_coords_from_line_list(
                            adjusted_polygon_lines)
                        room_polygon = ValidationHelper.check_if_polygon_was_recreated(
                            adjusted_room_coords, annotation[0][1])
                        boundary_lines = adjusted_polygon_lines
            if not boundary_lines:
                boundary_lines = line_coords_and_lengths_of_polygon['all_lines']
            separated_points = ExtractionHelper.separate_inner_points(
                room_coords, room_polygon)
            outer_polygon_points = separated_points['outer_points']
            inner_polygon_points = separated_points['inner_points']

            inner_lines = ExtractionHelper.get_lines_of_polygon(
                inner_polygon_points)
            area_calculated = round(room_polygon.area, 2)
            # check if area annotation approximately matches calculated room area
            area_annotation = annotation[2][1].replace('.', '').replace(',', '.', 1).replace(' m²', '') \
                .replace(' qm', '')
            area_diff = False
            if area_annotation == '':
                area_diff = True
            elif abs(float(area_annotation) - area_calculated) > 1:
                area_diff = True
            if (area_check_standard and area_annotation != '' and abs(float(area_annotation) - area_calculated) < 3) \
                    or (not area_check_standard and not check_line_matching) or \
                    (check_line_matching and area_annotation != '' and abs(float(area_annotation) - area_calculated) < 3)\
                    or (check_line_matching and area_annotation == ''):
                perimeter = ExtractionHelper.calculate_perimeter_with_arcs(ValidationHelper.substitute_boundary_lines_with_arcs
                                                                           (boundary_line_list_polygon=ValidationHelper.get_line_objects_of_polygon(
                                                                               polygon_points=room_coords),
                                                                               virt_arc_list_with_length=polygon_ext['arc_list_with_length']))
                perimeter_boundary_lines = room_polygon.length  # simple method from shapely
                if perimeter != perimeter_boundary_lines:
                    perimeter_diff = True
                else:
                    perimeter_diff = False
                line_coords_and_lengths_of_polygon = self.get_line_coords_and_length_of_polygon_with_virtual_entities(
                    polygon_with_virtual_entities=polygon_ext)
                room_number_location = (annotation[0][2], annotation[0][3])
                room_label_location = (annotation[1][2], annotation[1][3])
                area_location = (annotation[2][2], annotation[2][3])

                room_obj = {'room_id': "TEST", 'room_number': annotation[0][1],
                            'room_number_location': room_number_location, 'room_label': annotation[1][1],
                            'room_label_location': room_label_location, 'area_annotation': area_annotation,
                            'area_location': area_location, 'area_original': str(area_calculated),
                            'area_calculated': area_calculated, 'area_diff': area_diff, 'area_saved': '',
                            'perimeter_annotation': ' ', 'perimeter_location': ' ',
                            'perimeter_original': round(perimeter, 2),
                            'perimeter_calculated': round(perimeter_boundary_lines, 2),
                            'perimeter_diff': perimeter_diff, 'perimeter_saved': '',
                            'all_lines': line_coords_and_lengths_of_polygon['all_lines'],
                            'straight_lines': line_coords_and_lengths_of_polygon['straight_lines'],
                            'arc_lines': line_coords_and_lengths_of_polygon['arc_lines'],
                            'boundary_lines': boundary_lines, 'inner_lines': inner_lines,
                            'height': annotation[3][1],
                            'height_location': annotation[3][2],
                            'floor_covering': annotation[4][1], 'floor_covering_location': annotation[4][2],
                            'extracted_polygon_points': room_coords, 'outer_polygon_points': outer_polygon_points,
                            'inner_polygon_points': inner_polygon_points, 'manual_matching': manual_matching,
                            'polygon_id': polygon_ext['polygon_id']}
                return room_obj
            else:
                return None

    def get_line_coords_and_length_of_polygon_with_virtual_entities(self, polygon_with_virtual_entities: dict) -> dict:
        '''
        Description: Method to get line coordinates and length of polygon with virtual entities
        Params: polygon_with_virtual_entities: dict
        Return: line_coords_and_length: dict
        '''

        if type(polygon_with_virtual_entities) != dict:
            main_logger.warning(
                'Polygon has to be dict at getting line coordinates and length of polygon with virtual entities')
        elif list(polygon_with_virtual_entities.keys()) != ['polygon', 'all_line_list', 'straight_line_list_with_length',
                                                            'arc_list_with_length', 'polygon_id']:
            main_logger.warning('Polygon dict has to have following keys: polygon, all_line_list, straight_line_list_with_length, '
                  'arc_list_with_length at getting line coordinates and length of polygon with virtual entities')
            return None
        else:
            all_lines = []
            straight_lines = []
            arc_lines = []
            for line in polygon_with_virtual_entities['all_line_list']:
                all_lines.append(
                    {'coords': list(line['line'].coords), 'length': line['length']})
            for line in polygon_with_virtual_entities['straight_line_list_with_length']:
                straight_lines.append(
                    {'coords': list(line['line'].coords), 'length': line['length']})
            for arc in polygon_with_virtual_entities['arc_list_with_length']:
                arc_lines.append(
                    {'coords': list(arc['arc'].coords), 'length': arc['length']})
            return {'all_lines': all_lines, 'straight_lines': straight_lines, 'arc_lines': arc_lines}


    def get_unmatched_annotations(self, annotations: list, matched_room_polygons_and_annotations: list):
        '''
        Description: Method to get unmatched annotations
        Params: annotations: list, matched_room_polygons_and_annotations: list
        Return: result: list
        '''

        result = []
        matched_room_numbers = []
        if not type(annotations) == list or not type(matched_room_polygons_and_annotations) == list:
            main_logger.warning('Parameter have to be lists at getting unmatched annotations')
            return None
        else:
            for matched_room_polygon_and_annotation in matched_room_polygons_and_annotations:
                matched_room_numbers.append(
                    matched_room_polygon_and_annotation['room_number'])
            for annotation in annotations:
                if not type(annotation) == list:
                    main_logger.warning(
                        'Annotation list has to contain list objects at getting unmatched annotations')
                    return None
                if annotation[0][1] not in matched_room_numbers:
                    result.append(annotation)
            return result


    def get_unmatched_polygons_with_virtual_entities(self, polygons_with_virtual_entities: list, matched_room_polygons_and_annotations: list) -> list[dict]:
        '''
        Description: Method to get unmatched rooms
        Params: polygons_with_virtual_entities: list, matched_room_polygons_and_annotations: list
        Return: result: list[dict]
        '''
        result = []
        matched_room_polygon_points = []
        if not type(polygons_with_virtual_entities) == list or not type(matched_room_polygons_and_annotations) == list:
            main_logger.warning('Parameter have to be lists at getting unmatched polygons')
            return None
        else:
            for matched_room_polygon_and_annotation in matched_room_polygons_and_annotations:
                matched_room_polygon_points.append(
                    matched_room_polygon_and_annotation["extracted_polygon_points"])
            for polygon_ext in polygons_with_virtual_entities:
                if type(polygon_ext) != dict:
                    main_logger.warning('Polygon hast to be a dict at getting unmatched polygons')
                    return None
                elif list(polygon_ext.keys()) != ['polygon', 'all_line_list', 'straight_line_list_with_length',
                                                  'arc_list_with_length', 'polygon_id']:
                    main_logger.warning('Polygon dict has to have following keys: polygon, all_line_list, straight_line_list_with_length,'
                          'arc_list_with_length at getting unmatched polygons')
                    return None
                converted_matched_room_polygon_points = []
                for polygon_points in matched_room_polygon_points:
                    converted_polygon_points = []
                    for coordinates in polygon_points:
                        converted_polygon_points.append(
                            (coordinates[0], coordinates[1]))
                    converted_matched_room_polygon_points.append(
                        converted_polygon_points)
                if list(polygon_ext["polygon"].exterior.coords) not in converted_matched_room_polygon_points:
                    result.append(polygon_ext)
            return result


    def matching_via_line(self, open_annotations: list, lines_to_annotations: list, polygons_with_virtual_entities: list) -> list[dict]:
        '''
        Description: Method to match annotations and rooms via line
        Params: open_annotations: list, lines_to_annotations: list, polygons_with_virtual_entities: list
        Return: result: list[dict]
        '''

        result = []
        if type(open_annotations) != list or type(lines_to_annotations) != list or \
                type(polygons_with_virtual_entities) != list:
            main_logger.warning(
                'Not all parameters are lists at machting annotations and rooms via line')
            return None
        else:
            matched_lines_and_annotations = self.match_lines_and_annotations(open_annotations=open_annotations,
                                                                             lines_to_annotations=lines_to_annotations)
            for match in matched_lines_and_annotations:
                for polygon_ext in polygons_with_virtual_entities:
                    room = polygon_ext['polygon']
                    annotation = match['annotation']
                    if (room.contains(ShapelyPoint(match['line']['start_location'])) and
                        match['chosen_point'] == 'end') or \
                            (room.contains(ShapelyPoint(match['line']['end_location'])) and
                             match['chosen_point'] == 'start'):
                        room_obj = self.create_room_object(polygon_ext, annotation, area_check_standard=False,
                                                           check_line_matching=True, manual_matching=False)
                        if room_obj is not None:
                            result.append(room_obj)
                            polygons_with_virtual_entities.remove(polygon_ext)
            return result


    def match_lines_and_annotations(self, open_annotations: list, lines_to_annotations: list) -> list[dict]:
        '''
        Description: Method to match lines and annotations
        Params: open_annotations: list, lines_to_annotations: list
        Return: result: list[dict]
        '''

        result = []
        if type(open_annotations) != list or type(lines_to_annotations) != list:
            main_logger.warning('Not all parameters are lists at matching lines and annotations')
            return None
        else:
            for annotation in open_annotations:
                matched = {}
                minimal_distance = 2
                for line in lines_to_annotations:
                    new_distance_start_point_x = annotation[1][2]
                    new_distance_start_point_y = annotation[1][3]
                    new_distance_start_point = ShapelyPoint(new_distance_start_point_x, new_distance_start_point_y).distance(
                        ShapelyPoint((line['start_location'])))
                    new_distance_end_point_x = annotation[1][2]
                    new_distance_end_point_y = annotation[1][3]
                    new_distance_end_point = ShapelyPoint(new_distance_end_point_x, new_distance_end_point_y).distance(
                        ShapelyPoint((line['end_location'])))
                    if new_distance_start_point < new_distance_end_point:
                        if new_distance_start_point < minimal_distance:
                            minimal_distance = new_distance_start_point
                            matched = {'distance': minimal_distance, 'annotation': annotation, 'line': line,
                                       'chosen_point': 'start'}
                    else:
                        if new_distance_end_point < minimal_distance:
                            minimal_distance = new_distance_end_point
                            matched = {'distance': minimal_distance, 'annotation': annotation, 'line': line,
                                       'chosen_point': 'end'}
                    if (lines_to_annotations.index(line) + 1) == len(lines_to_annotations) and minimal_distance < 2 \
                            and matched != {}:
                        result.append(matched)

            return result
