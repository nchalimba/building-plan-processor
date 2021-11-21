
from app.main.constants import ACCEPTABLE_AREA_DEVIATION
from app.main.dtos.response.report_dto import ReportDto
from app.main.models.architecture_plan import Architecture_Plan
from app.main.models.polygon import Polygon
from app.main.models.simple_plan import Simple_Plan
from app.main.reporting.adjacent_plotter import AdjacentPlotter
from app.main.reporting.area_plotter import AreaPlotter
from app.main.reporting.facade_plotter import FacadePlotter
from app.main.reporting.matched_walls_plotter import MatchedWallsPlotter
from app.main.reporting.pdf_writer import PdfWriter
from app.main.reporting.perimeter_plotter import PerimeterPlotter
from app.main.reporting.reporting_constants import PLOT_CONTENT
from app.main.reporting.reporting_models import (AreaData, AreaTableRow,
                                                 ExtractedFunctionalities,
                                                 PerimeterData,
                                                 PerimeterTableRow, Plot,
                                                 ReportingPayload)
from app.main.reporting.unmatched_room_plotter import UnmatchedRoomPlotter
from app.main.reporting.wall_plotter import WallPlotter
from app.main.reporting.window_pillar_plotter import WindowPillarPlotter
from app.test.test_data.perimeter_validation import get_all_expect_perimeters
from loguru import logger

main_logger = logger.bind()

'''
Description: This class coordinates the creation of the report and all plots
'''

class ReportingService:

    def create_report(self, simple_plan: Simple_Plan, extracted_functionalities: ExtractedFunctionalities, log_messages: list, architecture_plan: Architecture_Plan = None) -> ReportDto:
        '''
        Description: This method coordinates the creation of relevant plots and the report.
        Params: imple_plan: Simple_Plan, extracted_functionalities: ExtractedFunctionalities, log_messages: list, architecture_plan: Architecture_Plan
        Return: report_dto: ReportDto
        '''
        
        if architecture_plan:
            report_payload = self.calculate_report_payload(
                simple_plan, extracted_functionalities, log_messages, architecture_plan)
        else:
            report_payload = self.calculate_report_payload(
                simple_plan, extracted_functionalities, log_messages)

        pdf_writer = PdfWriter()
        report_path = pdf_writer.create_flowable_pdf(report_payload)
        if not extracted_functionalities.outer_walls:
            report_payload.outer_wall_plot = None
        if not extracted_functionalities.match_room:
            report_payload.unmatched_room_plot = None
        if not extracted_functionalities.area:
            report_payload.area_plot = None
        if not extracted_functionalities.perimeter:
            report_payload.perimeter_plot = None
        if not extracted_functionalities.orientation:
            report_payload.orientation_plot = None
        if not extracted_functionalities.neighbours:
            report_payload.neighbour_plot = None
        if not extracted_functionalities.architecture_light_walls and not extracted_functionalities.architecture_load_bearing_walls:
            report_payload.architecture_walls_plot = None
        if not extracted_functionalities.architecture_pillars and not extracted_functionalities.architecture_windows:
            report_payload.architecture_pillars_and_windows_plot = None
        if not extracted_functionalities.architecture_facade_arcs and not extracted_functionalities.architecture_facade_lines:
            report_payload.architecture_facade_plot = None
        return report_payload.convert_to_dto(report_path)


    def calculate_report_payload(self, simple_plan: Simple_Plan, extracted_functionalities: ExtractedFunctionalities, log_messages: list, architecture_plan: Architecture_Plan = None) -> ReportingPayload:
        '''
        Description: This method calculates all data and creates all plots for the report.
        Params: simple_plan: Simple_Plan, extracted_functionalities: ExtractedFunctionalities, log_messages: list, architecture_plan: Architecture_Plan
        Return: reporting_payload: ReportingPayload
        '''
        
        # set all plots to None so we have only one return statement
        outer_wall_plot, unmatched_room_plot, area_plot, perimeter_plot, orientation_plot, neighbour_plot, matched_walls_plot, window_pillar_plot, facade_plot = (None, None, None, None, None, None, None, None, None)
        
        if extracted_functionalities.outer_walls:
            outer_wall_plot = None
            main_logger.info("create outer_wall_plot")
            wall_plotter = WallPlotter()
            outer_wall_plot_filepath = wall_plotter.plot_walls(
                simple_plan.polygons)
            outer_wall_plot = Plot(
                outer_wall_plot_filepath, PLOT_CONTENT["OUTER_WALL"]["PLOT_TITLE"],
                PLOT_CONTENT["OUTER_WALL"]["PLOT_CAPTION"])

        if extracted_functionalities.area:
            main_logger.info("create miscalculated_area_plot")
            area_plotter = AreaPlotter()
            area_data = self.create_area_data(simple_plan)
            area_plot_filepath = area_plotter.plot_miscalculated_room_area(
                simple_plan.polygons, area_data)
            area_plot = Plot(
                area_plot_filepath, PLOT_CONTENT["AREA"]["PLOT_TITLE"],
                PLOT_CONTENT["AREA"]["PLOT_CAPTION"])

        
        if extracted_functionalities.neighbours:
            main_logger.info("create adjacent_polygon_plot")
            adjacent_plotter = AdjacentPlotter()
            neighbour_plot_filepath = adjacent_plotter.plot_adjacent_polygons(
                simple_plan.polygons)
            neighbour_plot = Plot(
                neighbour_plot_filepath, PLOT_CONTENT["NEIGHBOUR"]["PLOT_TITLE"],
                PLOT_CONTENT["NEIGHBOUR"]["PLOT_CAPTION"])
       
        if extracted_functionalities.match_room:
            main_logger.info("create unmatched_roomstamp_plot")
            unmatched_room_plotter = UnmatchedRoomPlotter()
            unmatched_room_plot_filepath = unmatched_room_plotter.plot_unmatched_roomstamps(
                simple_plan.polygons, simple_plan.unmatched_rooms)
            unmatched_rooms = []
            for unmatched_room in simple_plan.unmatched_rooms:
                unmatched_rooms.append(unmatched_room[0][1])
            unmatched_room_plot = Plot(
                unmatched_room_plot_filepath, PLOT_CONTENT["UNMATCHED_ROOM"]["PLOT_TITLE"],
                PLOT_CONTENT["UNMATCHED_ROOM"]["PLOT_CAPTION"])
        
        if extracted_functionalities.perimeter:
            main_logger.info("create miscalculated_perimeter_plot")

            perimeter_plotter = PerimeterPlotter()
            perimeter_data = self.create_perimeter_data(simple_plan)
            perieter_plot_filepath = perimeter_plotter.plot_miscalculated_perimeter(
                simple_plan.polygons, perimeter_data)
            perimeter_plot = Plot(
                perieter_plot_filepath, PLOT_CONTENT["PERIMETER"]["PLOT_TITLE"],
                PLOT_CONTENT["PERIMETER"]["PLOT_CAPTION"])
        
        if extracted_functionalities.orientation:
            main_logger.info("create orientation_plot")
            orientation_plot_filepath = wall_plotter.plot_walls(
                simple_plan.polygons, is_orientation=True)
            orientation_plot = Plot(
                orientation_plot_filepath, PLOT_CONTENT["ORIENTATION"]["PLOT_TITLE"],
                PLOT_CONTENT["ORIENTATION"]["PLOT_CAPTION"])
        
        if extracted_functionalities.architecture_light_walls or extracted_functionalities.architecture_load_bearing_walls:
            main_logger.info("create matched_walls_plot")
            matched_walls_plotter = MatchedWallsPlotter()
            matched_walls_filepath = matched_walls_plotter.plot_walls(
                simple_plan.polygons)
            matched_walls_plot = Plot(
                matched_walls_filepath, PLOT_CONTENT["ARCHITECTURE_WALLS"]["PLOT_TITLE"],
                PLOT_CONTENT["ARCHITECTURE_WALLS"]["PLOT_CAPTION"])

        if extracted_functionalities.architecture_pillars or extracted_functionalities.architecture_windows:
            main_logger.info("create window and pillar plot")
            window_pillar_plotter = WindowPillarPlotter()
            window_pillar_plot_filepath = window_pillar_plotter.plot_window_and_pillar(
                polygons=simple_plan.polygons, architecture_plan=architecture_plan)
            window_pillar_plot = Plot(
                window_pillar_plot_filepath, PLOT_CONTENT["ARCHITECTURE_WINDOW_AND_PILLAR"]["PLOT_TITLE"],
                PLOT_CONTENT["ARCHITECTURE_WINDOW_AND_PILLAR"]["PLOT_CAPTION"])
        
        if extracted_functionalities.architecture_facade_lines or extracted_functionalities.architecture_facade_arcs:
            main_logger.info("create facade plot")
            facade_plotter = FacadePlotter()
            facade_plot_filepath = facade_plotter.plot_facade(architecture_plan, simple_plan.polygons)
            facade_plot = Plot(facade_plot_filepath, PLOT_CONTENT["ARCHITECTURE_FACADE"]["PLOT_TITLE"],
                PLOT_CONTENT["ARCHITECTURE_FACADE"]["PLOT_CAPTION"])

    
        return ReportingPayload(extracted_functionalities, unmatched_rooms, area_data, perimeter_data, log_messages,
                                outer_wall_plot=outer_wall_plot, unmatched_room_plot=unmatched_room_plot, area_plot=area_plot, 
                                perimeter_plot=perimeter_plot, orientation_plot=orientation_plot, neighbour_plot=neighbour_plot,
                                architecture_walls_plot=matched_walls_plot,architecture_pillars_and_windows_plot=window_pillar_plot,
                                architecture_facade_plot=facade_plot,plan_file_path=simple_plan.file_path, plan_file_name=simple_plan.file_name)
    

    def create_perimeter_data(self, simple_plan: Simple_Plan) -> PerimeterData:
        perimeter_table_rows = self.get_perimeter_table_rows(
            simple_plan.polygons)
        return(PerimeterData(len(perimeter_table_rows), perimeter_table_rows))

    def get_perimeter_table_rows(self, polygons: list[Polygon]) -> list[PerimeterTableRow]:
        expect_perimeter = get_all_expect_perimeters()
        
        perimeter_table_rows = []
        for polygon in polygons:
            polygon_id = polygon.id
            try:
                room_number = polygon.room.room_number
                perimter_calculated = float(polygon.perimeter)
                perimeter_validation = expect_perimeter.get(room_number)
                if perimeter_validation:
                    perimeter_validation = float(perimeter_validation)
                    perimeter_deviation = round(
                        abs((perimeter_validation - perimter_calculated) / perimeter_validation * 100), 2)
                    perimeter_table_rows.append(PerimeterTableRow(
                        room_number, round(perimter_calculated, 2), perimeter_validation, perimeter_deviation))
            except (KeyError, AttributeError):
                pass
        return perimeter_table_rows

    def create_area_data(self, simple_plan: Simple_Plan) -> AreaData:
        area_table_rows = self.get_area_table_rows(simple_plan.polygons)
        acceptable_deviation = int(ACCEPTABLE_AREA_DEVIATION * 100)
        amount_rooms = len(simple_plan.polygons)
        failure_rate = round(len(area_table_rows) / amount_rooms * 100, 2)
        amount_miscalculated_rooms = len(area_table_rows)

        return AreaData(amount_rooms, acceptable_deviation, amount_miscalculated_rooms, failure_rate, area_table_rows)

    def get_area_table_rows(self, polygons: list[Polygon]) -> list[AreaTableRow]:
        area_table_rows = []

        for polygon in polygons:
            polygon_id = polygon.id
            try:
                room_number = polygon.room.room_number
                area_calculated = float(polygon.area)
                area_annotation = float(polygon.room.room_area)
                area_deviation = abs(
                    (float(area_annotation) - float(area_calculated)) / float(area_annotation))
                if area_deviation >= ACCEPTABLE_AREA_DEVIATION:
                    area_table_rows.append(AreaTableRow(room_number, round(
                        area_calculated, 2), round(area_annotation, 2), round(area_deviation * 100, 2)))
            except (KeyError, AttributeError):
                pass
        return area_table_rows
