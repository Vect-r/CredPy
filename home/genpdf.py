#Generated on:151022-210757
#Author: Mitesh Vaid
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

class GenReport:
    def __init__(self,name):
        self.sdc=SimpleDocTemplate(name,pagesize=A4,rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0)
        styles=getSampleStyleSheet()
        self.paraStyles={'Head':ParagraphStyle('yourtitle',
                        fontName="Helvetica-Bold",
                        fontSize=22,parent=styles['Heading1'],
                        alignment=1,spaceAfter=14),
                        'Normal':ParagraphStyle('Date',alignment=1,parent=styles['Normal'])}
        self.elems=[]
        self.dwStyle=[('BACKGROUND',(2,0),(-3,-1),colors.pink),
                      ('BACKGROUND',(3,0),(-2,-1),colors.lightgreen),#for credit
                      ('FONTSIZE',(0,0),(-1,-1),14),
                      ('BOTTOMPADDING',(0,0),(-1,-1),7),
                      ('BOX',(0,0),(-1,0),0.25,colors.black),
                      ('BOX',(0,0),(-1,-1),1.0,colors.black),
                      ('BOX',(0,-1),(-1,-1),0.25,colors.black),
                      ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
                      ('ALIGN',(-1,0),(-1,-1),'RIGHT')]
        self.accStyle=[('BACKGROUND',(1,0),(-4,-1),colors.pink),
                            ('BACKGROUND',(2,0),(-3,-1),colors.lightgreen),
                            ('FONTSIZE',(0,0),(-1,-1),14),
                            ('RIGHTPADDING',(0,0),(-1,-1),38),
                            ('BOTTOMPADDING',(0,0),(-1,-1),7),
                            ('BOX',(0,0),(-1,0),0.25,colors.black),
                            ('BOX',(0,0),(-1,-1),1.0,colors.black),
                            ('BOX',(0,-1),(-1,-1),0.25,colors.black),
                            ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
                            ('ALIGN',(-1,0),(-1,-1),'RIGHT')]
        
    def Head(self,title):
        self.sdc.title=title
        self.elems.append(Paragraph(f"<h1>{title}</h1>",self.paraStyles['Head']))
        
    def singledate(self,fdate):
        self.elems.append(Paragraph(f"<p>As on <b>{fdate}</b>",self.paraStyles['Normal']))
        
    def daterange(self,fdate,edate):
        self.elems.append(Paragraph(f"<p><b>{fdate}</b> - <b>{edate}</b>",self.paraStyles['Normal']))
        
    #to generate DateWise Report
    def dwTable(self,data):
        self.elems.append(Table(data,style=self.dwStyle,repeatRows=1,spaceBefore=10))
    #to generate Particular Account Report
    def accTable(self,data):
        self.elems.append(Table(data,style=self.accStyle,repeatRows=1,spaceBefore=5))
    #finalyy
    def build(self):
        self.sdc.build(self.elems)
