import shutil
from dataclasses import dataclass, field
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.platypus.flowables import Preformatted


'''
    Building and testing add_table() method for PdfWriter
'''

PLOTS = {
    "SCALE": {
        "WIDTH": 4.2,
        "HEIGHT": 6
    }
}

TABLES = {
    "HEADER": {
        "AREA_TABLE": ['polygon id', 'room number',
                       'area annotation', 'area calculated', 'deviation in %'],
        "PERIMETER_TABLE": ['polygon id', 'room number',
                            'perimeter calculated', 'perimeter actual', 'perimeter deviation']
    },
    "SCALE": {
        "COL": 1.3,
        "ROW": 0.3
    }
}

#############################################################
######################    Example Data    ###################
#############################################################


@dataclass
class AreaTableRow:
    polygon_id: str
    room_number: str
    area_calculated: float
    area_annotation: float
    area_deviation: float


@dataclass
class PerimeterTableRow:
    polygon_id: str
    room_number: str
    perimeter_calculated: float
    perimeter_actual: float
    perimeter_deviation: float


@dataclass
class AreaData:
    amount_rooms: int
    acceptable_deviation: int
    amount_miscalculated_rooms: int
    failure_rate: int
    area_table_rows: list[AreaTableRow]


@dataclass
class PerimeterData:
    amount_rooms: int
    perimeter_table_rows: list[PerimeterTableRow]


# Area Data
area_table_row_1 = AreaTableRow("polygonId1234", "R 0.120", 57.72, 61.67, 6.84)
area_table_row_2 = AreaTableRow("polygonId4567", "R 0.806", 4.69, 5.05, 7.76)
area_table_row_3 = AreaTableRow("polygonId8910", "R 0.201", 8.34, 4.06, 8.12)

area_table_list = [area_table_row_1, area_table_row_2, area_table_row_3]
area_data = AreaData(1, 1, 1, 1, area_table_list)

# Perimeter Data
perimeter_table_row_1 = PerimeterTableRow(
    "polygonId1234", "R 0.120", 10, 61.67, 3.62)
perimeter_table_row_2 = PerimeterTableRow(
    "polygonId4567", "R 0.806", 12, 5.05, 2.87)
perimeter_table_row_3 = PerimeterTableRow(
    "polygonId4567", "R 0.806", 15, 1.4, 7.76)

perimeter_table_list = [perimeter_table_row_1,
                        perimeter_table_row_2, perimeter_table_row_3]
perimeter_data = PerimeterData(1, perimeter_table_list)


#############################################################
####################      Document    #######################
#############################################################
report_name = "test_extraction_report.pdf"
source = "test_extraction_report.pdf"
destination = "output/reporting"

doc = SimpleDocTemplate(report_name, pagesize=A4,
                        rightMargin=72, leftMargin=72,
                        topMargin=72, bottomMargin=18, title="TestExtractionTable")

Story = []

#############################################################
####################   Table Design    ######################
#############################################################
# table header in reporting_constants.py
# cols in reporting_constants.py


def add_table_area(table_data: list[AreaTableRow]):
    table_header = generate_table_header('area')
    data_prepared = prepare_table_data(table_data)

    data_prepared.insert(0, table_header)

    # number of rows and cols in table
    n_rows = len(data_prepared)
    n_cols = len(data_prepared[0])

    t = Table(data_prepared, n_cols *
              [TABLES["SCALE"]["COL"]*inch], n_rows*[TABLES["SCALE"]["ROW"]*inch])
    t.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, 0), 1, colors.black), ]))
    Story.append(t)


def add_table_perimeter(table_data: list[PerimeterTableRow]):
    table_header = generate_table_header('perimeter')
    data_prepared = prepare_table_data(table_data)

    data_prepared.insert(0, table_header)

    # number of rows and cols in table
    n_rows = len(data_prepared)
    n_cols = len(data_prepared[0])

    t = Table(data_prepared, n_cols *
              [TABLES["SCALE"]["COL"]*inch], n_rows*[TABLES["SCALE"]["ROW"]*inch])
    t.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, 0), 1, colors.black), ]))
    Story.append(t)

def add_table(table_data: list, useCase: str):
    table_header = generate_table_header(useCase)
    data_prepared = prepare_table_data(table_data)

    data_prepared.insert(0, table_header)

    # number of rows and cols in table
    n_rows = len(data_prepared)
    n_cols = len(data_prepared[0])

    t = Table(data_prepared, n_cols *
              [TABLES["SCALE"]["COL"]*inch], n_rows*[TABLES["SCALE"]["ROW"]*inch])
    t.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, 0), 1, colors.black), ]))
    Story.append(t)


def prepare_table_data(table_data: list):
    table_data_prepared = []

    # generate list of lists for table content
    for i in range(len(table_data)):
        a = table_data[i].__dict__.values()
        RowList = list(a)
        table_data_prepared.append(RowList)

    return table_data_prepared


def generate_table_header(useCase: str):

    if useCase == 'area':
        table_header = TABLES["HEADER"]["AREA_TABLE"]

        return table_header
    elif useCase == 'perimeter':
        table_header = TABLES["HEADER"]["PERIMETER_TABLE"]
        return table_header
    else:
        return None


#add_table_area(area_data.area_table_rows)
add_table(area_data.area_table_rows, 'area')

s = Spacer(80, 40)
Story.append(s)

add_table(perimeter_data.perimeter_table_rows, 'perimeter')

#add_table_perimeter(perimeter_data.perimeter_table_rows)


#table_data = area_data.area_table_rows
# print(dir(table_data[0]))
# print(table_data[0].__dict__.values())

# build PDF
doc.build(Story)

# move PDF to output/reporting
shutil.move(source, destination)
