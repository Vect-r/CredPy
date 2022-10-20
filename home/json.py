from models import CashBook
from models import CustomerAcc

def data2json(uid,name):
	p={}
	for i in CashBook.objects.filter(AccNo=uid,AccName=name):
		p[i.TranID]={'TranID':i.TranID,
			  		 'AccNo':i.AccNo,
			  		 'AccName':i.AccName,
			  		 'DrAmnt':i.DrAmnt,
			  		 'CrAmnt':i.CrAmnt,
			  		 'Desc':i.Desc,
			  		 'Date':i.Date,
			  		 'Time':i.Time}
	return p

if __name__=="__main__":
	print(data2json(1,"Mitesh Vaid"))