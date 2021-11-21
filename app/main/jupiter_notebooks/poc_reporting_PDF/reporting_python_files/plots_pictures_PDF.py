import shutil
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.units import inch

'''
    Generates an Test PDF file with 4 embedded plots named "test_extraction_report.pdf" 
    in directory "../output/reporting" for reporting (Extraction Report).
     
'''

report_name = "test_extraction_report.pdf"
source = "test_extraction_report.pdf"
destination = "output/reporting"

# standard A4 PDF
report = SimpleDocTemplate(report_name,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

# ExtractionReport and paths to plots and pictures
# 4 example plots in .png format
ExtractionReport = []
plot_path_1 = "app/main/jupiter_notebooks/reporting_PDF/test_png_plots_pictures/outer_walls_R-Bau_D_EG.png"
plot_path_2 = "app/main/jupiter_notebooks/reporting_PDF/test_png_plots_pictures/neighbouring_rooms.png"
plot_path_3 = "app/main/jupiter_notebooks/reporting_PDF/test_png_plots_pictures/room_example_1.png"
plot_path_4 = "app/main/jupiter_notebooks/reporting_PDF/test_png_plots_pictures/room_example_2.png"

# path and scale of polt or image
plot_1 = Image(plot_path_1, width=4.2*inch, height=6*inch)
plot_2 = Image(plot_path_2, width=4.2*inch, height=6.4*inch)
plot_3 = Image(plot_path_3, width=4.2*inch, height=7*inch)
plot_4 = Image(plot_path_4, width=4.2*inch, height=7*inch)

# append plots to PDF
ExtractionReport.append(plot_1)
ExtractionReport.append(plot_2)
ExtractionReport.append(plot_3)
ExtractionReport.append(plot_4)

# build PDF
report.build(ExtractionReport)

# move PDF to output/reporting
shutil.move(source, destination)
