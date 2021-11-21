import shutil
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


'''
    Building and testing add_table() method for PdfWriter
'''

report_name = "test_extraction_report.pdf"
source = "test_extraction_report.pdf"
destination = "output/reporting"

#############################################################
####################      Document    ####################### 
#############################################################
doc = SimpleDocTemplate(report_name, pagesize=A4,
                        rightMargin=72, leftMargin=72,
                        topMargin=72, bottomMargin=18, title="TestExtractionTable")

elements = []

#############################################################
####################   Table Data    ######################## 
#############################################################

#Room Number
#area annotation
#area claculated
#deviation in %

data= [['Room number', 'area annotation', 'area calculated', 'deviation in %'],
['R 0.120', 57.72, 61.67, 6.84],
['R 0.120', 57.72, 61.67, 6.84],
['R 0.120', 57.72, 61.67, 6.84]]

#############################################################
####################   Table Design    ###################### 
#############################################################
t=Table(data,4*[1.6*inch], 4*[0.3*inch])

'''
t.setStyle(TableStyle([('ALIGN',(1,1),(-2,-2),'RIGHT'),
('TEXTCOLOR',(1,1),(-2,-2),colors.red),
('VALIGN',(0,0),(0,-1),'TOP'),
('TEXTCOLOR',(0,0),(0,-1),colors.blue),
('ALIGN',(0,-1),(-1,-1),'CENTER'),
('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
('TEXTCOLOR',(0,-1),(-1,-1),colors.green),
('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
('BOX', (0,0), (-1,-1), 0.25, colors.black),
]))
'''

t.setStyle(TableStyle([('LINEBELOW',(0,0),(-1,0),1,colors.black),
]))

#elements.append(t)

# build PDF
doc.build(elements)

# move PDF to output/reporting
shutil.move(source, destination)