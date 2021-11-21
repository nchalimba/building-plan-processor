from dataclasses import dataclass, field
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

'''
    Building and testing add_plot() method for PdfWriter
'''

#############################################################
#################      Example Plots    ##################### 
#############################################################

@dataclass
class Plot:
    plot_path: str
    plot_title: str
    plot_caption: str
    polygon_id: str = field(default=None)


plot_path_owp = "app/main/jupiter_notebooks/reporting_PDF/test_png_plots_pictures/outer_walls_R-Bau_D_EG.png"
plot_path_area_1 = "app/main/jupiter_notebooks/reporting_PDF/test_png_plots_pictures/neighbouring_rooms.png"
plot_path_area_2 = "app/main/jupiter_notebooks/reporting_PDF/test_png_plots_pictures/room_example_1.png"

# example plots
outer_wall_plot = Plot(plot_path_owp, "Outer Wall Plot",
                       "Abbildung 1", "polyid1234")

area_plots = [Plot(plot_path_area_1, "Area Plot", "Abbildung 2", "polyid1234"), Plot(
    plot_path_area_2, "Area Plot", "Abbildung 3", "polyid1234")]


#############################################################
####################      Document    ####################### 
#############################################################

report_name = "test_extraction_report.pdf"

doc = SimpleDocTemplate(report_name, pagesize=A4,
                        rightMargin=72, leftMargin=72,
                        topMargin=72, bottomMargin=18, title="Test")
Story = []


#############################################################
####################     Methods      ####################### 
#############################################################

def add_plot_single(plot_single: Plot, scale: tuple):
    # add single plot with variable scale to Extraction Report PDF
    # for example: outer_wall_plot, orientation_plot, neighbour_plot

    extraction_plot = Image(plot_single.plot_path,
                            width=scale[0], height=scale[1])
    # append plots to PDF
    Story.append(extraction_plot)
    print("Appended single plot")


def add_plot_multiple(plot_multiple: list[Plot], scale: tuple):
    # add multiple plots to Extraction PDF
    # for example: unmatched_room_plots, area_plots

    for plot in plot_multiple:
        extraction_plot = Image(plot.plot_path, width=scale[0], height=scale[1])
        Story.append(extraction_plot)

    print("Appended multiple plots")


add_plot_single(outer_wall_plot, (4.2*inch, 6*inch))
add_plot_multiple(area_plots, (4.2*inch, 6*inch))

# build PDF
doc.build(Story)
