from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from app.main.reporting.reporting_constants import TEXT_FONTS

class HeaderFooterCanvas(canvas.Canvas):


    def __init__(self, pagesize: str):
        ''' 
        Description: This method determines the dimensions of the page
        Params: pagesize: string
        Returns: none
        Exceptions: none
        '''

        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    def draw_header(self):
        ''' 
        Description: This method creates the Header for the extraction Report
        Returns: none 
        Exceptions: none
        '''

        page = "NuData Backend"
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setFont('Times-Roman', TEXT_FONTS['PARAGRAPH'])
        self.drawCentredString(A4[0]/2, A4[1]-20, page)
        self.restoreState()

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        ''' 
        Description: This method gets the page and page count
        Returns: none 
        Exceptions: none
        '''

        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_footer(page_count)
            self.draw_header()

            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_count: int):
        ''' 
        Description: This method creates the Footer for the extraction Report
        Params: page_count: integer
        Returns: none 
        Exceptions: none
        '''

        page = "Page %s of %s" % (self._pageNumber, page_count)
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setFont('Times-Roman', TEXT_FONTS['PARAGRAPH'])
        self.drawCentredString(A4[0]/2, 20, page)
        self.restoreState()