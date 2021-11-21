
REPORT_LINE_SPACER = 12
REPORT_RIGHT_MARGIN = 72 
REPORT_LEFT_MARGIN = 72
REPORT_TOP_MARGIN = 72
REPORT_BOTTOM_MARGIN = 18

TEXT_FONTS = {
    'TITLE': 22,
    'SUBTITLE': 16,
    'SUB_SUBTITLE': 14,
    'PARAGRAPH': 10,
    'IMAGE_TITLE': 9
}

# Scaling of plots that are embedded in the PDF
# optimal scaling for EG, 1OG and 2OG in PDF
PLOTS = {
    "SCALE": {
        "WIDTH": 8,
        "HEIGHT": 4.5
    }
}

# Table header depending on the table type and row/column scale
TABLES = {
    "HEADER": {
        "AREA_TABLE": ['room number',
                       'area annotation', 'area calculated', 'deviation in %'],
        "PERIMETER_TABLE": ['room number',
                            'perimeter calculated', 'perimeter actual', 'perimeter deviation']
    },
    "SCALE": {
        "COL": 1.5,
        "ROW": 0.2
    }
}

STATIC_CONSTANTS = {
    "MAIN_PAGE": {
        "TITLE": "Extraction Report",
        "TIMESTAMP_PREFIX": "Timestamp: ",
        "PAGE_TEMPLATE": "Page <start> of <end>",
        "FIRST_PARAGRAPH": "This extraction report provides an overview of the results of the backend extraction process. Supported plan types are SimplePlan (SP) and ArchitecturePlan (AP). At the current time, the following extraction options are supported:",
        "EXTRACTION_OPTIONS": {
            "OUTER_WALLS": "(SP) Outer Walls",
            "MATCH_ROOM": "(SP) Matched Room Annotations:",
            "AREA": "(SP) Area:",
            "PERIMETER": "(SP) Perimeter:",
            "ORIENTATION": "(SP) Orientation:",
            "NEIGHBOURS": "(SP) Neighbours:",
            "ARCHITECTURE_LIGHT_WALLS": "(AP) Light Walls",
            "ARCHITECTURE_LOAD_BEARING_WALLS": "(AP) Load Bearing Walls",
            "ARCHITECTURE_PILLARS": "(AP) Pillars",
            "ARCHITECTURE_WINDOWS": "(AP) Windows",
            "ARCHITECTURE_FACADE_ARCS": "(AP) Facade Arcs",
            "ARCHITECTURE_FACADE_LINES": "(AP) Facade Lines"
        },
        "LOG_SUBTITLE": "Extraction Log",
    },
    "OUTER_WALLS": {
        "SUBTITLE": "Outer Walls",
        "SUB_SUBTITLE": "Visual presentation:",
    },
    "MATCH_ROOM": {
        "SUBTITLE": "Matched Room Annotations with Polygons",
        "PARAGRAPH": "The following room annotations were not matched:",
        "SUB_SUBTITLE": "Visual presentation:",
    },
    "AREA": {
        "SUBTITLE": "Area (annotation area vs. calculated area)",
        "PARAGRAPHS": {
            "AMOUNT_ROOMS": "rooms in simple plan <filename>:",
            "ACCEPTABLE_DEVIATION": "acceptable area deviation (%):",
            "AMOUNT_MISCALCULATED_ROOMS": "Counted rooms where annotation area not calculated area:",
            "FAILURE_RATE": "Failure rate (%):"
        },
        "SUB_SUBTITLE": "Visual presentation:",
    },
    "PERIMETER": {
        "SUBTITLE": "Perimeter",
        "SUB_SUBTITLE": "Visual presentation",
        "ROOM_COUNT_LABEL": "rooms for validation:",
    },
    "ORIENTATION": {
        "SUBTITLE": "Orientation",
        "SUB_SUBTITLE": "Visual presentation:",
    },
    "NEIGHBOURS": {
        "SUBTITLE": "Neighbour Rooms",
        "SUB_SUBTITLE": "Visual presentation:",
    },
    "ARCHITECTURE_WALLS": {
        "SUBTITLE": "Matching: Architecture Walls",
        "SUB_SUBTITLE": "Visual presentation:",
    },
    "ARCHITECTURE_WINDOW_AND_PILLAR": {
        "SUBTITLE": "Matching: Windows and Pillars",
        "SUB_SUBTITLE": "Visual presentation:",
    },
    "ARCHITECTURE_FACADE": {
        "SUBTITLE": "Facade",
        "SUB_SUBTITLE": "Visual presentation:",
    }
}


PLOT_CONTENT = {
    "OUTER_WALL": {
        "PLOT_TITLE": "Visualisierung der Außenwände",
        "PLOT_CAPTION": "Außenwände von <filename>"
    },
    "UNMATCHED_ROOM": {
        "PLOT_TITLE": "Visualisierung der nicht zugeordneten Raumstempel",
        "PLOT_CAPTION": "Nicht zugeordnete Räume von <filename>"
    },
    "AREA": {
        "PLOT_TITLE": "Visualisierung der Räume mit falsch berechneten Flächen",
        "PLOT_CAPTION": "Falsch berechnete Flächen von <filename>"
    },
    "PERIMETER": {
        "PLOT_TITLE": "Visualisierung der Räume mit falsch berechnetem Umfang",
        "PLOT_CAPTION": "Falsch berechnete Umfänge von <filename>"
    },
    "ORIENTATION": {
        "PLOT_TITLE": "Visualisierung der Orientierung der Außenwände",
        "PLOT_CAPTION": "Orientierung der Wände von <filename>"
    },
    "NEIGHBOUR": {
        "PLOT_TITLE": "Visualisierung der Nachbarn aller Räume",
        "PLOT_CAPTION": "Nachbarräume von <filename>"
    },
    "ARCHITECTURE_WALLS": {
        "PLOT_TITLE": "Visualisierung der Architecture Walls",
        "PLOT_CAPTION": "matched walls von <filename>"
    },
    "ARCHITECTURE_WINDOW_AND_PILLAR": {
        "PLOT_TITLE": "Visualisierung der Architecture Windows & Pillars",
        "PLOT_CAPTION": "architecture entities von <filename>"
    },
    "ARCHITECTURE_FACADE": {
        "PLOT_TITLE": "Visualisierung der Fassade",
        "PLOT_CAPTION": "facade entities von <filename>"
    }
}
