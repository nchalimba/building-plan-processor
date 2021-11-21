import os
from datetime import datetime
from enum import Enum
from sys import platform as _platform

# check if outline polygon (bgf) has innerloops
# point(x0), check next N points(xN) if x0.distanceTo(xN) is lt. 0.0001 -> loop
IDENTIFY_LOOPS_IN_OUTLINE_POLYGON = True
IDENTIFY_LOOPS_IN_OUTLINE_POLYGON_RANGE = 20 # Tested: 0, 20, 40, 60 

ENABLE_OUTER_WALLS = True
ENABLE_NEIGHBOURS = True

# Generate Walls
ENABLE_CLOSE_POLYGONS = True
ENABLE_SIMPLE_PILLAR_KILL = True
ENABLE_COMPLEX_PILLAR_KILL = True
ENABLE_POINT_ON_LINE_KILL = False # macht alles schlimmer
ENABLE_EDGES_KILL = True # funktioniert gut
EDGE_THRESHOLD = 0.35 #0.5

# Neighbour Rooms
DISTANCE_TO_NEIGHBOURS = 0.75 # Tested 3.0 / 1.5 / 1.0 / 0.75 

# Room Geometry
COORDINATE_THRESHOLD_BULGE_VALUE_MIN = -0.99
COORDINATE_THRESHOLD_BULGE_VALUE_MAX = 0.99

# Orientation prioritization
COMPASS_ORIENTATION_PRIORITIZED = True

# NuData - R-Bau_D_*.dxf layers
NUDATA_LAYER_RAUMPOLYGON = "RAUMPOLYGON"
NUDATA_LAYER_RAUMSTEMPEL = "RAUMSTEMPEL"
NUDATA_LAYER_BGF = "BGF"

# NuData - R-Bau_D_*.dxf attributes
NUDATA_ATTRIBUTE_RAUMNUMMER = "RAUMNUMMER"
NUDATA_ATTRIBUTE_RAUMBEZEICHNUNG = "RAUMBEZEICHNUNG"

# NuData - Compass
NUDATA_COMPASS_LAYOUT = "Bestandsplan"

# unittests
ACCEPTABLE_AREA_DEVIATION = 0.05
ACCEPTABLE_PERIMETER_DEVIATION = 0.05
TEST_POLYGON_INDEX = 9
TEST_POLYGON_INDEX_GENERATE_WALLS = 30

# should be 0... 
AREA_INCORRECT_EG = 17 
AREA_INCORRECT_1OG = 13 
AREA_INCORRECT_2OG = 7 

# app.test.test_perimeter
PERIMETER_INCORRECT_EG = 3 
PERIMETER_INCORRECT_1OG = 6 
PERIMETER_INCORRECT_2OG = 9 

# app.test.test_annotations
ANNOTATION_NOT_MATCHED_EG = 2 
ANNOTATION_NOT_MATCHED_1OG = 1 
ANNOTATION_NOT_MATCHED_2OG = 3 

# app.test.test_neighbour
NEIGHBOUR_INCORRECT_EG = 0 
NEIGHBOUR_INCORRECT_1OG = 7 
NEIGHBOUR_INCORRECT_2OG = 1 #R 2.094 is not extracted correctly 

# app.test.test_generate_walls_new # todo: one generate_walls_test
WALL_INCORRECT_EG = 28 #(55) 
WALL_INCORRECT_1OG = 19 #(45) 
WALL_INCORRECT_2OG = 20 #(40) 

# app.test.test_outerwall
OUTERWALL_INCORRECT_EG = 45 
OUTERWALL_INCORRECT_1OG = 47
OUTERWALL_INCORRECT_2OG = 46

# detect os and set output path on application startup
if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
    REPORT_SAVE_DIRECTORY = os.getcwd() + "/output/reporting/"
    PLOT_SAVE_DIRECTORY = os.getcwd() + "/output/files/"
elif _platform == "win32" or _platform == "win64":
    REPORT_SAVE_DIRECTORY = os.getcwd() + "\\output\\reporting\\"
    PLOT_SAVE_DIRECTORY = os.getcwd() + "\\output\\files\\"
    

TIME_STAMP_FORMAT = "%Y%m%d_%H_%M_%S"

REPORT_TIME_STAMP_FORMAT = "%B %d, %Y - %H:%M:%S"


# Plots
PLOT_DPI = 900
PLOT_LINE_WIDTH_SMALL = 0.1
PLOT_LINE_WIDTH_NORMAL = 0.2
PLOT_LINE_WIDTH_LARGE = 0.4
PLOT_LINE_WIDTH_HUGE = 0.8


class PlotStyle(Enum):
    AXIS = "both"
    TICKS_LEFT = False
    TICKS_BOTTOM = False
    LABEL_LEFT = False
    LABEL_BOTTOM = False
    TRANSPARENT = True
    ROOM_LABEL_SIZE = 6
    ROOM_LABEL_Y_POS = 15 # plot room label on y - 15

class PlotTypes(Enum):
    OUTER_WALL_PLOT = "Aussenwand"
    WALL_PLOT = "Waende"
    POLYGON_PLOT = "Polygone"
    OUTER_WALL_ORIENTATION_PLOT = "Aussenwand_Orientierung"
    ROOM_NUMBER_PLOT = "Raumnummern"
    UNMATCHED_ROOM_PLOT = "Unmatched_Rooms"
    ADJACENT_PLOT = "Angrenzende_Raeume"
    AREA_PLOT = "Flachenberechnung"
    PERIMETER_PLOT = "Umfangsberechnung"
    ARCHITECTURE_WALLS_PLOT = "Architektenplan_Waende"
    ARCHITECTURE_PILLARS_AND_WINDOWS_PLOT = "Architektenplan_Saeulen_und_Fenster"
    ARCHITECTURE_FACADE_PLOT = "Architektenplan_Fassaden"

#REDIS
QUEUE = "extraction"

class OrientationColors(Enum):
    NORTH = "black"
    NORTH_EAST = "red"
    EAST = "darkorange"
    SOUTH_EAST = "yellow"
    SOUTH = "lime"
    SOUTH_WEST = "cyan"
    WEST = "blue"
    NORTH_WEST = "fuchsia"

class NeighbourColors(Enum):
    LESS_THAN_ONE = "yellow"
    LESS_THAN_TWO = "red"
    LESS_THAN_FOUR = "lime"
    LESS_THAN_SIX = "black"
    LESS_THAN_EIGHT = "darkorange"
    MORE_THAN_EIGHT = "fuchsia"

class DefaultColors(Enum):
    GREEN = "tab:green"
    RED = "tab:red"
    GRAY = "tab:gray"
    CYAN = "tab:cyan"
    PINK = "tab:pink"
    BROWN = "tab:brown"

class MatchedWallStyle(Enum):
    LINESTYLE_SOLID = "solid"
    SOLID_RANGE = " 0-15 cm"
    LINESTYLE_DOTTED = "dotted"
    DOTTED_RANGE = " 15-20 cm"
    LINESTYLE_DASHED = "dashed"
    DASHED_RANGE = " 20-25 cm"
    LINESTYLE_DASHDOT = "dashdot"
    DASHDOT_RANGE = " 25-35 cm"
    UNKNOWN_RANGE = " unknown"

#MATCHING
MATCHING_SCALE_THRESHOLD = {
    "UPPER": 1.05,
    "LOWER": 0.95
}
SMALL_WALL_LINE_THRESHOLD = 0.22 # Schwellwert unter dem eine Architektenwand als kleine Wand erkannt wird
DEFAULT_WALL_THICKNESS = 0.25 
MAX_WINDOW_RADIUS = 2.0 # Maximaler Radius zur Erkennung von Fenstern
FACADE_LAYER = "A_05_FASSADE_ELEMENTE"
PILLAR_LAYER = "A_01_STUETZE"
FACADE_ARC_MIN_LINE_LENGTH = 0.5 # Minimale Länge von aus Arcs erzeugten Linien
LIGHT_WALL_LAYER = "A_02_LEICHTWAND"
LOAD_BEARING_WALL_LAYER = "A_01_TRAGWAND"
MAX_WINDOW_DISTANCE = 0.5 # Schwellwert der Distanz zum Matchen von Fenstern
PILLAR_DISTANCE_THRESHOLD = 0.00104 # Schwellwert zum Matchen der Säulen (plus radius)
INTERSECTING_LINE_THRESHOLD = 0.1 # Schwellwert für Distanz, unter der angenommen wird, dass zwei Linien sich schneiden
WINDOW_LENGTH_THRESHOLD = 1.2 # Distanz, unter der angenommen wird, dass ein Punkt von der Fassade auf einer Wand liegt oder umgekehrt
FIRST_LEVEL_X_OFFSET = -161.2638 # x-Kooridanten-Offset zw. simpleplan und architectureplan 1.OG
FIRST_LEVEL_Y_OFFSET = -20.533 # y-Kooridanten-Offset zw. simpleplan und architectureplan 1.OG
SECOND_LEVEL_X_OFFSET = -56.6477 # x-Kooridanten-Offset zw. simpleplan und architectureplan 2.OG
SECOND_LEVEL_Y_OFFSET = 11.7208 # y-Kooridanten-Offset zw. simpleplan und architectureplan 2.OG
MATCHING_OFFSET_THRESHOLD = {
    "UPPER": 0.5,
    "LOWER": -0.5
}
FIRST_LEVEL_X_OFFSET_VALIDATION = -162.42619174739457 # x-Kooridanten-Offset zw. simpleplan und architectureplan 1.OG für die validierung
FIRST_LEVEL_Y_OFFSET_VALIDATION = -30.59378946948694 # y-Kooridanten-Offset zw. simpleplan und architectureplan 1.OG für die validierung
SECOND_LEVEL_X_OFFSET_VALIDATION = -57.7755409382344 # x-Kooridanten-Offset zw. simpleplan und architectureplan 2.OG für die validierung
SECOND_LEVEL_Y_OFFSET_VALIDATION = -50.11507491329723 # y-Kooridanten-Offset zw. simpleplan und architectureplan 2.OG für die validierung
GROUND_LEVEL_X_OFFSET_VALIDATION = -1.4451228967093925 # x-Kooridanten-Offset zw. simpleplan und architectureplan EG für die validierung
GROUND_LEVEL_Y_OFFSET_VALIDATION = -7.660081174141801 # y-Kooridanten-Offset zw. simpleplan und architectureplan EG für die validierung
FIRST_LEVEL_FILE_NAME = "R-Bau_A_1OG.dxf" # Dateiname des ersten Stockwerkes
SECOND_LEVEL_FILE_NAME = "R-Bau_A_2OG.dxf" # Dateiname des zweiten Stockwerkes


ENABLE_CUSTOM_OFFSET = False #Aktiviert das Matching von Plänen, die einen individuellen Offset haben
CUSTOM_X_OFFSET = 0.0
CUSTOM_Y_OFFSET = 0.0


class MATCHED_WALL_TYPES(Enum):
    LOAD_BEARING_WALL = "load-bearing wall"
    LIGHT_WALL = "light wall"

AVAILABLE_PLAN_TYPES = ["simple_plan", "architecture_plan", "combined_plan"]



ENABLE_NEW_GENERATE_WALLS = True