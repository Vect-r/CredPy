#Generated on:131022-115348#Author: Mitesh Vaid
#Description: LedPy custom Report Generation object using reportlab
#Under BETA
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import Table, TableStyle, Frame
from reportlab.lib import colors

class GenReport:
    def __init__(self,name):
        self.cnvs=canvas.Canvas(name,pagesize=A4)
        
    def showCords(self):
        #for Debugging to be removed on final Phase
        self.cnvs.setFont('Helvetica-Bold',11)
        for i in range(0,1000,20):
            self.cnvs.drawString(i,830,str(i))
        for j in range(0,1000,20):
            self.cnvs.drawString(2,j,str(j))
            
    def save(self):
        self.cnvs.save()
    
    def drawNameHead(self,head:str):
        self.cnvs.setFont("Helvetica-Bold", 22)        
        self.cnvs.drawCentredString(300,800,head)
        self.cnvs.setTitle(head)
             
    def textDate(self,fdate,tdate):
        self.cnvs.setFont("Helvetica",10)
        self.cnvs.drawCentredString(300,780,f"From {fdate} To {tdate}")
    
    def fTable(self,data):
        #self.cnvs.setFont("Helvetica-Bold", 11)        
        t=Table(data,style=[('BACKGROUND',(1,0),(-4,-1),colors.pink),
                            ('BACKGROUND',(2,0),(-3,-1),colors.lightgreen),
                            ('FONTSIZE',(0,0),(-1,-1),14),
                            #('RIGHTPADDING',(0,0),(-1,-1),38),
                            ('BOTTOMPADDING',(0,0),(-1,-1),7),
                            ('BOX',(0,0),(-1,0),0.25,colors.black),
                            ('BOX',(0,0),(-1,-1),1.0,colors.black),
                            ('BOX',(0,-1),(-1,-1),0.25,colors.black),
                            ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
                            ('ALIGN',(-1,0),(-1,-1),'RIGHT')],repeatRows=1)
        f=Frame(10,20,580,760)
        f.addFromList([t],self.cnvs)


class ReportPDF:
    def __init__(self,name):
        self.sdc=SimpleDocTemplate(name,pagesize=A4)

    def drTable(self,data):
        style=[#('BACKGROUND',(,0),(-4,-1),colors.pink),
               #('BACKGROUND',(),(0,-2),colors.lightgreen),
                ('FONTSIZE',(0,0),(-1,-1),14),
                #('RIGHTPADDING',(0,0),(-1,-1),38),
                ('BOTTOMPADDING',(0,0),(-1,-1),7),
                ('BOX',(0,0),(-1,0),0.25,colors.black),
                ('BOX',(0,0),(-1,-1),1.0,colors.black),
                ('BOX',(0,-1),(-1,-1),0.25,colors.black),
                ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
                ('ALIGN',(-1,0),(-1,-1),'RIGHT')]
        t=Table(data,style=style,repeatRows=1)
        elements=[]
        elements.append(t)
        self.sdc.build(elements)
