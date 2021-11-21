import os
import time
from datetime import datetime

from app.main.constants import (REPORT_SAVE_DIRECTORY,
                                REPORT_TIME_STAMP_FORMAT, TIME_STAMP_FORMAT)
from app.main.reporting.header_footer import HeaderFooterCanvas
from app.main.reporting.reporting_constants import *
from app.main.reporting.reporting_models import (AreaData, AreaTableRow,
                                                 ExtractedFunctionalities,
                                                 LogMessage, PerimeterData,
                                                 PerimeterTableRow, Plot,
                                                 ReportingPayload)
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

'''
Description: This class contains the main logic to create the pdf extraction report.
'''
class PdfWriter:
    

    def create_flowable_pdf(self, report_data: ReportingPayload) -> str:
        '''
        Description: This method contains the logic to automatically create the extraction report.
        Params: self: PdfWriter, report_data: ReportingPayload
        Return: filename: str
        '''

        filename = self.create_file_name()
        doc = SimpleDocTemplate(filename, pagesize=A4,
                                rightMargin=REPORT_RIGHT_MARGIN, leftMargin=REPORT_LEFT_MARGIN,
                                topMargin=REPORT_TOP_MARGIN, bottomMargin=REPORT_BOTTOM_MARGIN, title=STATIC_CONSTANTS['MAIN_PAGE']['TITLE'])
        Story = []
        reporting_subtitle_number = 1
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

        # Start story
        title = '<font size="20">%s</font>' % STATIC_CONSTANTS['MAIN_PAGE']['TITLE']
        Story.append(Paragraph(title, styles["Title"]))
        Story.append(Spacer(1, REPORT_LINE_SPACER))

        now = datetime.now()
        timestamp = "{} {}".format(STATIC_CONSTANTS["MAIN_PAGE"]["TIMESTAMP_PREFIX"], now.strftime(
            REPORT_TIME_STAMP_FORMAT))
        self.add_paragraph_with_spacer(Story, timestamp)

        self.add_paragraph_with_spacer(
            Story, STATIC_CONSTANTS['MAIN_PAGE']['FIRST_PARAGRAPH'])
        extraction_options_number = 1
        for key in STATIC_CONSTANTS['MAIN_PAGE']['EXTRACTION_OPTIONS']:
            data = getattr(report_data.extracted_functionalities, key.lower())
            data = u'\u2714' if data else u'\u2716'
            text = "{}. {}".format(str(extraction_options_number), STATIC_CONSTANTS['MAIN_PAGE']['EXTRACTION_OPTIONS'][key])
            self.add_paragraph(
                Story, "{} {}".format(text, str(data)))
            extraction_options_number += 1

        self.add_subtitle(Story, STATIC_CONSTANTS['MAIN_PAGE']['LOG_SUBTITLE'], 0)
        for log_message in report_data.log_messages:
            self.add_paragraph_with_spacer(Story, str(log_message))

        self.add_page_break(Story)

        # outer walls
        if report_data.extracted_functionalities.outer_walls:
            self.add_subtitle(Story, STATIC_CONSTANTS['OUTER_WALLS']['SUBTITLE'], reporting_subtitle_number)
            reporting_subtitle_number += 1
            self.add_sub_subtitle(Story, STATIC_CONSTANTS['OUTER_WALLS']['SUB_SUBTITLE'])
            self.add_plot_single(
                Story, report_data.outer_wall_plot, (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)

        # matched room annotations
        if report_data.extracted_functionalities.match_room:
            self.add_subtitle(Story, STATIC_CONSTANTS['MATCH_ROOM']['SUBTITLE'], reporting_subtitle_number)
            reporting_subtitle_number += 1
            self.add_paragraph_with_spacer(
                Story, STATIC_CONSTANTS['MATCH_ROOM']['PARAGRAPH'])
            self.add_paragraph_with_spacer(Story, str(report_data.unmatched_rooms))
            self.add_sub_subtitle(Story, STATIC_CONSTANTS['MATCH_ROOM']['SUB_SUBTITLE'])
            self.add_plot_single(
                Story, report_data.unmatched_room_plot, (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)

        # area
        if report_data.extracted_functionalities.area:
            self.add_subtitle(Story, STATIC_CONSTANTS['AREA']['SUBTITLE'], reporting_subtitle_number)
            reporting_subtitle_number += 1
            for paragraph in STATIC_CONSTANTS['AREA']['PARAGRAPHS']:
                data = getattr(report_data.area_data, paragraph.lower())
                self.add_paragraph(Story, "{} {}".format(
                    STATIC_CONSTANTS['AREA']['PARAGRAPHS'][paragraph], str(data)))
            
            Story.append(Spacer(1, REPORT_LINE_SPACER))
            self.add_table(Story, report_data.area_data.area_table_rows, 'area')
            self.add_sub_subtitle(Story, STATIC_CONSTANTS['AREA']['SUB_SUBTITLE'])
            self.add_plot_single(Story, report_data.area_plot,
                                (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)

        # perimeter
        if report_data.extracted_functionalities.perimeter:
            self.add_subtitle(Story, STATIC_CONSTANTS['PERIMETER']['SUBTITLE'], reporting_subtitle_number)
            reporting_subtitle_number += 1
            self.add_paragraph_with_spacer(
                Story, "{} {}".format(STATIC_CONSTANTS['PERIMETER']['ROOM_COUNT_LABEL'].replace("<filename>", filename),
                                    report_data.perimeter_data.amount_rooms))
            self.add_table(Story, report_data.perimeter_data.perimeter_table_rows, 'perimeter')
            self.add_sub_subtitle(Story, STATIC_CONSTANTS['PERIMETER']['SUB_SUBTITLE'])
            self.add_plot_single(Story, report_data.perimeter_plot,
                                (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)

        # orientation
        if report_data.extracted_functionalities.orientation:
            self.add_subtitle(Story, STATIC_CONSTANTS['ORIENTATION']['SUBTITLE'], reporting_subtitle_number)
            reporting_subtitle_number += 1
            if report_data.orientation_plot.plot_path == "ERROR":
                self.add_paragraph(Story,"Orientation plot could not be created")
            else:
                self.add_sub_subtitle(Story, STATIC_CONSTANTS['ORIENTATION']['SUB_SUBTITLE'])
                self.add_plot_single(
                    Story, report_data.orientation_plot, (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)

        # neighbour
        if report_data.extracted_functionalities.neighbours:
            self.add_subtitle(Story, STATIC_CONSTANTS['NEIGHBOURS']['SUBTITLE'], reporting_subtitle_number)
            reporting_subtitle_number += 1
            self.add_sub_subtitle(Story, STATIC_CONSTANTS['NEIGHBOURS']['SUB_SUBTITLE'])
            self.add_plot_single(
                Story, report_data.neighbour_plot, (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)
        
        # architecture walls
        if report_data.extracted_functionalities.architecture_load_bearing_walls or report_data.extracted_functionalities.architecture_light_walls:
            self.add_subtitle(Story, STATIC_CONSTANTS['ARCHITECTURE_WALLS']['SUBTITLE'], reporting_subtitle_number)
            reporting_subtitle_number += 1
            self.add_sub_subtitle(Story, STATIC_CONSTANTS['ARCHITECTURE_WALLS']['SUB_SUBTITLE'])
            self.add_plot_single(
                Story, report_data.architecture_walls_plot, (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)

        # architecture windows and pillars
        if report_data.extracted_functionalities.architecture_pillars or report_data.extracted_functionalities.architecture_windows:
            self.add_subtitle(Story, STATIC_CONSTANTS['ARCHITECTURE_WINDOW_AND_PILLAR']['SUBTITLE'], reporting_subtitle_number)
            reporting_subtitle_number += 1
            self.add_sub_subtitle(Story, STATIC_CONSTANTS['ARCHITECTURE_WINDOW_AND_PILLAR']['SUB_SUBTITLE'])
            self.add_plot_single(
                Story, report_data.architecture_pillars_and_windows_plot, (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)

        # architecture facade arcs and lines
        if report_data.extracted_functionalities.architecture_facade_arcs or report_data.extracted_functionalities.architecture_facade_lines:
            self.add_subtitle(Story, STATIC_CONSTANTS["ARCHITECTURE_FACADE"]["SUBTITLE"], reporting_subtitle_number)
            reporting_subtitle_number += 1
            self.add_sub_subtitle(Story, STATIC_CONSTANTS['ARCHITECTURE_FACADE']['SUB_SUBTITLE'])
            self.add_plot_single(
                Story, report_data.architecture_facade_plot, (PLOTS["SCALE"]["WIDTH"]*inch, PLOTS["SCALE"]["HEIGHT"]*inch))
            self.add_page_break(Story)
        doc.multiBuild(Story, canvasmaker=HeaderFooterCanvas)
        return filename

    def create_file_name(self) -> str:
        '''
        Description: This method creates a file name for the report containing a timestamp.
        Returns: file_name: str
        '''
        now = datetime.now()
        date_time = now.strftime(TIME_STAMP_FORMAT)
        return REPORT_SAVE_DIRECTORY + "report_" + date_time + ".pdf"

    def add_paragraph(self, Story: list, text: str):
        '''
        Description: This method adds a paragraph to the given story.
        Params: Story: list, text: str
        '''
        ptext = '<font size="%s">%s</font>' % (TEXT_FONTS['PARAGRAPH'], text)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        Story.append(Paragraph(ptext, styles["Justify"]))

    def add_paragraph_with_spacer(self, Story: list, text: str):
        '''
        Description: This method adds a paragraph including a spacer to the given story.
        Params: Story: list, text: str
        '''
        self.add_paragraph(Story, text)
        Story.append(Spacer(1, REPORT_LINE_SPACER))

    def add_subtitle(self, Story: list, text: str, number: int):
        '''
        Description: This method adds a subtitle to the given story with a given subtitle number.
        Params: Story: list, text: str, number: int
        '''
        text_with_number = "{}. {}".format(str(number), text)
        ptext = '<font size="%s">%s</font>' % (TEXT_FONTS['SUBTITLE'], text_with_number)
        styles = getSampleStyleSheet()
        Story.append(Paragraph(ptext, styles["Heading2"]))
        Story.append(Spacer(1, REPORT_LINE_SPACER))

    def add_sub_subtitle(self, Story: list, text: str):
        '''
        Description: This method adds a sub subtitle to the given story.
        Params: Story: list, text: str
        '''
        ptext = '<font size="%s">%s</font>' % (
            TEXT_FONTS['SUB_SUBTITLE'], text)
        styles = getSampleStyleSheet()
        Story.append(Paragraph(ptext, styles["Heading3"]))
        Story.append(Spacer(1, REPORT_LINE_SPACER))

    def add_page_break(self, Story: list):
        '''
        Description: This method adds a page break to the given story.
        Params: Story: list
        '''
        Story.append(PageBreak())

    
    def add_plot_single(self, Story: list, plot_single: Plot, scale: tuple):
        '''
        Description: This method adds single plot with variable scale to PDF for example: outer_wall_plot, orientation_plot, neighbour_plot.
        Params: Story: list, plot_single: Plot, scale: tuple
        Return: -
        '''

        if(self.is_plot_file_path_valid(plot_single.plot_path)):

            extraction_plot = Image(plot_single.plot_path,
                                    width=scale[0], height=scale[1])
            Story.append(extraction_plot)
            return

        self.add_paragraph(
            Story, "File {} not found".format(plot_single.plot_path))

    def add_plot_multiple(self, Story: list, plot_multiple: list[Plot], scale: tuple):
        '''
        Description: This method adds multiple plots to PDF for example: unmatched_room_plots, area_plots.
        Params: Story: list, plot_multiple: list[Plot], scale: tuple
        Return: -
        '''

        for plot in plot_multiple:
            extraction_plot = Image(
                plot.plot_path, width=scale[0], height=scale[1])
            Story.append(extraction_plot)

    def is_plot_file_path_valid(self, file_path: str) -> bool:
        '''
        Description: This method checks whether a given file path contains a valid plot.
        Params: file_path: str
        Return: is_valid: bool
        '''
        return os.path.exists(file_path) and (
            file_path[-4:] == ".png" or file_path[-4:] == ".jpeg"
            or file_path[-4:] == ".jpg")

    def add_table(self, Story: list, table_data: list, useCase: str):
        '''
        Description: This method adds tables to PDF.
        Params: Story: list, table_data: list, useCase: str
        Return: -
        '''

        table_header = self.generate_table_header(useCase)
        data_prepared = self.prepare_table_data(table_data)

        data_prepared.insert(0, table_header)

        n_rows = len(data_prepared)
        n_cols = len(data_prepared[0])

        t = Table(data_prepared, n_cols *
                  [TABLES["SCALE"]["COL"]*inch], n_rows*[TABLES["SCALE"]["ROW"]*inch])
        t.setStyle(TableStyle(
            [('LINEBELOW', (0, 0), (-1, 0), 1, colors.black), ]))
        Story.append(t)

    def prepare_table_data(self, table_data: list) -> list:
        '''
        Description: This method prepares data for insertion into the table.
        Params: table_data: list
        Return: table_data_prepared: list
        '''

        table_data_prepared = []

        # generate list of lists for table content
        for i in range(len(table_data)):
            a = table_data[i].__dict__.values()
            RowList = list(a)
            table_data_prepared.append(RowList)
        return table_data_prepared

    def generate_table_header(self, useCase: str) -> str:
        '''
        Description: This methods generates a table header depending on the table type.
        Params: useCase: str
        Return: table_header: Any
        '''
        
        if useCase == 'area':
            table_header: str = TABLES["HEADER"]["AREA_TABLE"]
            return table_header
        elif useCase == 'perimeter':
            table_header: str = TABLES["HEADER"]["PERIMETER_TABLE"]
            return table_header
        else:
            return None


if __name__ == "__main__":
    '''
    Description: This logic builds a mock report
    '''
    extracted_functionalities = ExtractedFunctionalities(
        outer_walls=True, match_room=True, area=True, perimeter=True, neighbours=True)
    outer_wall_plot = Plot("testtest.png",
                           "test test", "Abbildung: ...", "polyid1234")
    unmatched_room_plot = Plot(
        "testtest.png", "test test", "Abbildung ..." "polyid1234")
    unmatched_rooms = ["R 0.051", "R 0.905"]
    area_rows = [AreaTableRow("234", "R 0.051", 1234, 1234, 123)]
    area_data = AreaData(250, "5%", 50, str(50/250) + "%", area_rows)
    area_plot = Plot("testtest.png", "test test", "abbildung ...", "polyid1234")
    perimeter_rows = [PerimeterTableRow("234", "R 0.051", 1323, 213, 134)]
    perimeter_data = PerimeterData(250, perimeter_rows)
    perimeter_plot = Plot("testtest.png",
                          "test test", "Abbildung: ...", "polyid1234")
    log_messages = []
    log_messages.append(LogMessage(
        "INFO", "The following plan was successfully read in", "R-Bau_D_EG.dxf"))
    orientation_plot = Plot("testtest.png", "test test",
                            "Abbildung ...", "polyid1234")
    neighbour_plot = Plot("testtest.png", "test test",
                          "Abbildung ...", "polyid1234")
    plan_file_path = "testtesttest.dxf"
    payload = ReportingPayload(extracted_functionalities, outer_wall_plot, unmatched_room_plot, unmatched_rooms,
                               area_data, area_plot, perimeter_data, perimeter_plot, log_messages, orientation_plot, neighbour_plot, plan_file_path)
    rooms = ["R 0.051", "R 0.905"]

    pdfwriter = PdfWriter()
    pdfwriter.create_flowable_pdf(payload)
