from django.shortcuts import render, HttpResponse, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from django.contrib.auth.models import User
from django.contrib.auth import logout,authenticate,login
#from django.conf import settings
from django.template.loader import get_template, render_to_string
#from django.contrib.staticfiles import finders
from django.http import FileResponse,HttpResponseRedirect, JsonResponse
#from django.views.decorators.csrf import csrf_exempt
from datetime import datetime as dt
from .models import *
from .genpdf import *
#from django.core import serializers
from json import dumps
#import os
import io

ref=None

# Create your views here.
def loginUser(request):
	if request.method=="POST":
		usernm=request.POST.get('username')
		passwd=request.POST.get('passwd')
		user=authenticate(username=usernm,password=passwd)

		if user is not None:
			login(request,user)
			return redirect('/')
		else:
			return render(request,'login.html',context={'stat':"showError()"})

	return render(request,'login.html')



def fetchall():
	no=[i.AccID for i in CustomerAcc.objects.all()]
	#name=[i.FullName for i in CustomerAcc.objects.all()]
	data=[fetchBalance(i) for i in [CashBook.objects.filter(AccNo=i) for i in no]]
	return {i:x for i,x in zip(no,data)}


def logoutUser(request):
	logout(request)
	return redirect('/login')

def index(request):
	if request.user.is_anonymous:
		return redirect('/login')

	ctx = {}
	url_parameter = request.GET.get("q")

	if url_parameter:
		data=CustomerAcc.objects.filter(FullName__icontains=url_parameter).values_list('AccID','FullName','LastBalance')
	else:
		data=CustomerAcc.objects.all().values_list('AccID','FullName','LastBalance')

	ctx["accounts"] = data
	does_req_accept_json = request.accepts("application/json")
	is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json

	if is_ajax_request:
		html = render_to_string(template_name="collection.html", context={"accounts": data})
		data_dict = {"html_from_view": html}
		return JsonResponse(data=data_dict, safe=False)

	#updateBalanceAll()
	data=CustomerAcc.objects.values_list('AccID','FullName','LastBalance')
	return render(request,'index.html',context=ctx)


def updateBalanceAll():
	p=fetchall()
	for i in p.keys():
		try:
			bal=p[i][-1]
		except IndexError:
			bal="0"
		g=CustomerAcc.objects.get(AccID=i)
		g.LastBalance=bal
		g.save(update_fields=['LastBalance'])


def updateBalanceQuery(accid):
	p=fetchBalance(CashBook.objects.filter(AccNo=accid))
	i=CustomerAcc.objects.get(AccID=accid)
	try:
		bal=p[-1]
	except IndexError:
		bal="0"
	#print('Update Bal: ',bal)
	i.LastBalance=bal
	i.save(update_fields=['LastBalance'])


'''

def bac(request):
	o=[]
	key=readKey()

	for i in CustomerAcc.objects.all():
		o.append('INSERT INTO home_customeracc (FullName,phno,Address,Email,DateCreated,TimeCreated) VALUES ("{}","{}","{}","{}","{}")'.format(i.AccID,i.FullName,i.Address,i.phno,i.Email,i.DateCreated.strftime('%y-%m-%d')))
	o.append('')

	for i in CashBook.objects.all():
		o.append('INSERT INTO home_cashbook (TranID,AccNo,AccName,DrAmnt,CrAmnt,Desc,Date,Time) VALUES \
			("{}","{}","{}","{}","{}","{}","{}","{}")'.format(i.TranID,i.AccNo.AccID,i.AccName,i.DrAmnt,i.CrAmnt,i.Desc,i.Date.strftime('%y-%m-%d'),i.Time.strftime('%H:%M:%S')))
	o.append('')

	for i in LastBalance.objects.all():
		o.append(f'INSERT INTO home_lastbalance (Account_id,Balance) VALUES ("{i.Account.AccID}","{i.Balance}")')


	encrypted = key.encrypt(stringify(o).encode(),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
	file=io.BytesIO(encrypted)
	file.seek(0)
	return FileResponse(file,as_attachment=True,filename="dncv.io21on")

def stringify(d):
	k=""
	for i in d: k+=f'{i}\n'
	return k

def readKey():
    with open("public_key.pem", "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read(),backend=default_backend())
'''

def about(request):
	return render(request,'about.html')

def cdate():
	return dt.now().strftime("%Y-%m-%d")

def cdatefrmt():
	return dt.now().strftime("%d.%m.%Y")

def ctime():
	return dt.now().strftime('%H:%m:%S')

def addTran(request,uid):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method == "POST":
		tranid=lastidINC()
		#str : "Jan 01, 2023"
		date=dt.strptime(request.POST.get("Cdate"),'%b %d, %Y').strftime('%Y-%m-%d')
		try:
			CrAmnt=int(request.POST.get("CrAmnt"))
		except:
			CrAmnt=0

		try:
			DrAmnt=int(request.POST.get("DrAmnt"))
		except:
			DrAmnt=0
		Desc=request.POST.get("desc")
		name=getname(uid)
		AccNo=CustomerAcc.objects.get(AccID=uid)
		sub=CashBook(TranID=tranid,AccNo=AccNo,AccName=name,CrAmnt=CrAmnt,DrAmnt=DrAmnt,Desc=Desc,Date=date,Time=ctime())
		sub.save()
		updateBalanceQuery(uid)
		return redirect(f'/view/{uid}')

	return render(request,'addTran.html',{'cdate':cdate(),'name':getname(uid),'id':uid,'callback':f'/view/{uid}'})

def addQuick(request):
	if request.user.is_anonymous:
		return redirect('/login')

	data=dumps({i[0]:'/static/circle.png' for i in CustomerAcc.objects.all().values_list("FullName")})
	if request.method == "POST":
		print(request.POST)
		tranid=lastidINC()
		#str : "Jan 01, 2023"
		date=dt.strptime(request.POST.get("Cdate"),'%b %d, %Y').strftime('%Y-%m-%d')
		try:
			CrAmnt=int(request.POST.get("CrAmnt"))
		except:
			CrAmnt=0

		try:
			DrAmnt=int(request.POST.get("DrAmnt"))
		except:
			DrAmnt=0
		Desc=request.POST.get("desc")
		name=request.POST.get("fullname")
		AccNo=CustomerAcc.objects.get(FullName=name)
		sub=CashBook(TranID=tranid,AccNo=AccNo,AccName=name,CrAmnt=CrAmnt,DrAmnt=DrAmnt,Desc=Desc,Date=date,Time=ctime())
		sub.save()
		updateBalanceQuery(AccNo.AccID)
		return redirect(f'/addQuick')
		
	return render(request,'addQuick.html',{'data':data,'callback':'/'})

'''
@csrf_exempt
def addTranAPI(request):
	tranid=lastidINC()
	uid=request.POST.get('uid')
	date=request.POST.get('Cdate')
	CrAmnt=request.POST.get('CrAmnt')
	DrAmnt=request.POST.get('DrAmnt')
	AccNo=CustomerAcc.objects.get(AccID=uid,FullName=request.POST.get('name'))
	name=AccNo.FullName
	Desc=request.POST.get('Desc')
	sub=CashBook(TranID=tranid,AccNo=AccNo,AccName=name,CrAmnt=CrAmnt,DrAmnt=DrAmnt,Desc=Desc,Date=date,Time=ctime())
	sub.save()
	updateBalanceQuery(uid)
	return JsonResponse({'status':'Transaction Added'},status=200)

@csrf_exempt
def addAccountAPI(request):
	if request.method=="POST":
		name=request.POST.get("name")
		address=request.POST.get("address")
		email=request.POST.get("e-mail")
		phno=request.POST.get("phno")
	submit=CustomerAcc(FullName=name,Address=address,phno=phno,Email=email,DateCreated=cdate(),TimeCreated=ctime())
	submit.save()
	return JsonResponse({'status':'Account Added!!!'},status=200)
'''

def lastidINC():
	try:
		p=int(CashBook.objects.last().TranID)+1
	except:
		p=1

	return p

def getname(uid):
	return CustomerAcc.objects.get(AccID=uid).FullName

'''
def viewAccount(request,uid,name):
	if request.user.is_anonymous:
		return redirect('/login')

	data=CustomerAcc.objects.get(AccID=uid,FullName=name)
	return render(request,'viewCustomer.html',{'data':data})
'''
def viewAccount(request,uid):
	if request.user.is_anonymous:
		return redirect('/login')

	data=CustomerAcc.objects.get(AccID=uid)
	return render(request,'viewCustomer.html',{'data':data,'callback':f'/view/{data.AccID}'})

def view(request,uid):
	if request.user.is_anonymous:
		return redirect('/login')

	sdate = request.GET.get('sdate')
	#print(sdate)
	edate = request.GET.get('edate')
	#print(edate)

	if (sdate!="" and sdate!=None) and (edate=="" and edate!=None):
		name=CustomerAcc.objects.get(AccID=uid).FullName
		lsb=CustomerAcc.objects.get(AccID=uid).LastBalance
		#return render(request,'viewTran.html',{'name':name,'lsb':lsb,'id':uid,'fdate':sdate,'edate':edate,'state':'Single'})
		#print('single')
		data=CashBook.objects.filter(AccNo=uid,Date=dt.strptime(sdate,'%b %d, %Y').strftime('%Y-%m-%d'))
		name=CustomerAcc.objects.get(AccID=uid).FullName
		lsb=CustomerAcc.objects.get(AccID=uid).LastBalance
		drttl=sum([i.DrAmnt  for i in data])
		crttl=sum([i.CrAmnt  for i in data])
		balance=fetchBalance(data)
		return render(request,'viewTran.html',{'name':name,'lsb':lsb,'id':uid,"data":zip(data,balance),'defdate':cdate(),"lastid":lastidINC(),'cr':crttl,'dr':drttl,'fdate':sdate})
	elif (sdate!="" and sdate!=None) and (edate!="" and edate!=None):
		name=CustomerAcc.objects.get(AccID=uid).FullName
		lsb=CustomerAcc.objects.get(AccID=uid).LastBalance
		#return render(request,'viewTran.html',{'name':name,'lsb':lsb,'id':uid,'fdate':sdate,'edate':edate,'state':'Double'})
		#print('double')
		data=CashBook.objects.filter(AccNo=uid,Date__range=[dt.strptime(sdate,'%b %d, %Y').strftime('%Y-%m-%d'),dt.strptime(edate,'%b %d, %Y').strftime('%Y-%m-%d')])
		name=CustomerAcc.objects.get(AccID=uid).FullName
		lsb=CustomerAcc.objects.get(AccID=uid).LastBalance
		drttl=sum([i.DrAmnt  for i in data])
		crttl=sum([i.CrAmnt  for i in data])
		balance=fetchBalance(data)
		return render(request,'viewTran.html',{'name':name,'lsb':lsb,'id':uid,"data":zip(data,balance),'defdate':cdate(),"lastid":lastidINC(),'cr':crttl,'dr':drttl,'fdate':sdate,'edate':edate})


	data=CashBook.objects.filter(AccNo=uid)
	name=CustomerAcc.objects.get(AccID=uid).FullName
	lsb=CustomerAcc.objects.get(AccID=uid).LastBalance
	drttl=sum([i.DrAmnt  for i in data])
	crttl=sum([i.CrAmnt  for i in data])
	balance=fetchBalance(data)
	updateBalanceQuery(uid)
	#print(balance)
	return render(request,'viewTran.html',{'name':name,'lsb':lsb,'id':uid,"data":zip(data,balance),'callback':f'/','defdate':cdate(),"lastid":lastidINC(),'cr':crttl,'dr':drttl})

def genPDF(request,uid):
	if request.user.is_anonymous:
		return redirect('/login')

	sdate = request.GET.get('sdate')
	#print(sdate)
	edate = request.GET.get('edate')
	#print(edate)
	#print(request.GET)

	if (sdate!="" and sdate!=None) and (edate=="" and edate!=None):
		#print('single')
		name=CustomerAcc.objects.get(AccID=uid).FullName
		fname=f"{name}-{dt.strptime(sdate,'%b %d, %Y').strftime('%Y-%m-%d')}"
		data=CashBook.objects.filter(AccNo=uid,Date=dt.strptime(sdate,'%b %d, %Y').strftime('%Y-%m-%d'))
		balance=fetchBalance(data)
		n=0
	elif (sdate!="" and sdate!=None) and (edate!="" and edate!=None):
		#print('double')
		name=CustomerAcc.objects.get(AccID=uid).FullName
		fname=f"{name}.{dt.strptime(sdate,'%b %d, %Y').strftime('%d-%m-%Y')}_{dt.strptime(edate,'%b %d, %Y').strftime('%d-%m-%Y')}"
		data=CashBook.objects.filter(AccNo=uid,Date__range=[dt.strptime(sdate,'%b %d, %Y').strftime('%Y-%m-%d'),dt.strptime(edate,'%b %d, %Y').strftime('%Y-%m-%d')])
		balance=fetchBalance(data)
		n=1
	else:
		#print('none')
		data=CashBook.objects.filter(AccNo=uid)
		name=data[0].AccName
		fname=name
		balance=fetchBalance(data)
		n=0
	frmt=[[i.Date.strftime('%d/%m/%Y'),i.DrAmnt,i.CrAmnt,i.Desc,j] for i,j in zip(data,balance)]
	frmt.insert(0,['Date', 'Debit', 'Credit', 'Description', 'Balance'])
	ttl=retSum(data)
	frmt.append(['Total',ttl['Dr.'],ttl['Cr.'],'',balance[-1]])
	#print(frmt)
	buf=io.BytesIO()
	pdf=GenReport(buf)
	pdf.Head(name)
	if n==0:
		pdf.singledate(sdate)
	else:
		pdf.daterange(sdate,edate)
	pdf.accTable(frmt)
	pdf.build()
	buf.seek(0)
	return FileResponse(buf,as_attachment=True,filename=fname+'.pdf')

def update(request,tid):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method=="POST":
		callback=request.POST.get('next')
		if request.POST.get("vCrAmnt")=="":
			cr=0
		else:
			cr=request.POST.get('vCrAmnt')
		if request.POST.get("vDrAmnt")=="":
			dr=0
		else:
			dr=request.POST.get('vDrAmnt')
		name=request.POST.get('fullname')
		cb=CashBook.objects.get(TranID=tid)
		acc=CustomerAcc.objects.get(FullName=name)
		cb.AccNo=acc
		cb.AccName=name
		cb.CrAmnt=cr
		cb.DrAmnt=dr
		cb.Desc=request.POST.get("vdesc")
		cb.Date=dt.strptime(request.POST.get("vdate"),'%b %d, %Y').strftime('%Y-%m-%d')
		cb.save()
		updateBalanceQuery(cb.AccNo.AccID)
		#print(request.META.get('HTTP_REFERER'))
		#return redirect(f'/view/{cb.AccNo.AccID}')
		return redirect(callback)

	#print(request.GET.get('cbk'))
	names=data=dumps({i[0]:'/static/circle.png' for i in CustomerAcc.objects.all().values_list("FullName")})
	ref=request.META.get('HTTP_REFERER')
	data=CashBook.objects.get(TranID=tid)
	return render(request,'editTran.html',{'data':data,'callback':ref,'names':names})

def NoneChk(var):
	if type(var)==str:
		if len(var)>0: return True
		else: return False

def fetchBalance(query):
	p=[]
	c=0
	for i in query:
		if i.DrAmnt>0:
			c+=i.DrAmnt
		elif i.CrAmnt>0:
			c-=i.CrAmnt

		if c<-1:
			t="Cr."
		elif c==0:
			t='0'
		else:
			t="Dr."

		p.append(f'{abs(c)} {t}')

	return p

def reports(request):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method=="GET":
		#search=request.GET.get("search")

		fdate=request.GET.get("sdate")
		edate=request.GET.get("edate")


		if fdate=="" and edate=="":
			return render(request,'reports.html')
		elif fdate is not None and edate=="":
			#print('if')
			fdate=dt.strptime(request.GET.get("sdate"),'%b %d, %Y').strftime('%Y-%m-%d')
			d=CashBook.objects.filter(Date=fdate)
			p=retSum(d)
			return render(request,'reports.html',{'d':d,'fdate':fdate,'dr':p['Dr.'],'cr':p['Cr.']})
		elif fdate is not None and edate is not None:
			fdate=dt.strptime(request.GET.get("sdate"),'%b %d, %Y').strftime('%Y-%m-%d')
			edate=dt.strptime(request.GET.get("edate"),'%b %d, %Y').strftime('%Y-%m-%d')
			d=CashBook.objects.filter(Date__range=[fdate,edate])
			p=retSum(d)
			return render(request,'reports.html',{'d':d,'fdate':fdate,'edate':edate,'dr':p["Dr."],'cr':p['Cr.']})


	#d=CashBook.objects.all().order_by("-Date")
	#d=CashBook.objects.all().order_by('-Time').reverse()
	ent=CashBook.objects.all().order_by('-Time').order_by('-Date')
	page=request.GET.get('page',1)
	paginator=Paginator(ent,30)
	try:
		ents=paginator.page(page)
	except PageNotAnInteger:
		ents=paginator.page(1)
	except EmptyPage:
		ents=paginator.page(paginator.num_pages)
	#dlist=[i.FullName for i in CustomerAcc.objects.all()]
	ttl=retSum(ent)
	return render(request,'reports.html',{'d':ents,'dr':ttl['Dr.'],'cr':ttl['Cr.']})

def repdate(request):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method=="GET":
		#search=request.GET.get('search')
		fdate=request.GET.get('sdate')
		edate=request.GET.get('edate')
		s_fdate=request.GET.get('sdate')
		s_edate=request.GET.get('edate')

		#print(request.GET)

		if fdate=="" and edate=="":
			data=CashBook.objects.all()
			fdate=cdate()
			frmt=[[i.AccName,i.Date.strftime('%d/%m/%Y'),i.DrAmnt,i.CrAmnt,i.Desc] for i in data]
			frmt.insert(0,['Name','Date', 'Debit', 'Credit', 'Description',])
			ttl=retSum(data)
			frmt.append(['','Total',ttl['Dr.'],ttl['Cr.'],''])
			filename=f"CredPy_{cdatefrmt()}.pdf"


		elif fdate is not None and edate=="":
			fdate=dt.strptime(request.GET.get("sdate"),'%b %d, %Y').strftime('%Y-%m-%d')
			data=CashBook.objects.filter(Date=fdate)
			frmt=[[i.AccName,i.Date.strftime('%d/%m/%Y'),i.DrAmnt,i.CrAmnt,i.Desc] for i in data]
			frmt.insert(0,['Name','Date', 'Debit', 'Credit', 'Description',])
			ttl=retSum(data)
			frmt.append(['','Total',ttl['Dr.'],ttl['Cr.'],''])
			filename=f"CredPy_{fdate}.pdf"

		elif fdate!="" and edate!="":
			fdate=dt.strptime(request.GET.get("sdate"),'%b %d, %Y').strftime('%Y-%m-%d')
			edate=dt.strptime(request.GET.get("edate"),'%b %d, %Y').strftime('%Y-%m-%d')
			data=CashBook.objects.filter(Date__range=[fdate,edate])
			frmt=[[i.AccName,i.Date.strftime('%d/%m/%Y'),i.DrAmnt,i.CrAmnt,i.Desc] for i in data]
			frmt.insert(0,['Name','Date', 'Debit', 'Credit', 'Description',])
			ttl=retSum(data)
			frmt.append(['','Total',ttl['Dr.'],ttl['Cr.'],''])
			filename=f"CredPy_{fdate}_{edate}.pdf"

	#print(frmt)
	buf=io.BytesIO()
	pdf=GenReport(buf)
	pdf.Head('CredPy')
	if fdate and edate=="":
		pdf.singledate(s_fdate)
	else:
		pdf.daterange(s_fdate,s_edate)
	pdf.dwTable(frmt)
	pdf.build()
	buf.seek(0)
	return FileResponse(buf,as_attachment=True,filename=filename)


def delete(request,tranid):
	if request.user.is_anonymous:
		return redirect('/login')
	else:
		#print("del True")
		c=CashBook.objects.get(TranID=tranid)
		no=c.AccNo.AccID
		name=c.AccName
		c.delete()
		updateBalanceQuery(no)
		return redirect(f'/view/{no}')

def retSum(data):
	return {'Dr.':sum([i.DrAmnt for i in data]),'Cr.':sum([i.CrAmnt for i in data])}

def addAccount(request):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method=="POST":
		name=request.POST.get("name")
		address=request.POST.get("address")
		email=request.POST.get("e-mail")
		if len(request.POST.get('phno'))>1:
			phno=request.POST.get("phno")
		else:
			phno=0

		submit=CustomerAcc(FullName=name,Address=address,phno=phno,Email=email,DateCreated=cdate(),TimeCreated=ctime(),LastBalance="0")
		submit.save()
		return redirect('/')

	data=[i[0] for i in CustomerAcc.objects.all().values_list('FullName')]
	return render(request,'addCustomer.html',{'callback':f'/','data':data})


def deleteAccount(request,accid):
	if request.user.is_anonymous:
		return redirect('/login')

	#print(accid)
	c=CustomerAcc.objects.get(AccID=accid)
	c.delete()
	return redirect('/')


def editAccount(request,uid):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method=="POST":
		#accid=request.POST.get("accid")
		FullName=request.POST.get("name")
		p=CustomerAcc.objects.get(AccID=uid)
		pfull=p.FullName
		p.FullName=FullName
		p.Address=request.POST.get("address")
		p.Email=request.POST.get("e-mail")
		if request.POST.get("phno")=="":
			p.phno=0
		else:
			p.phno=request.POST.get("phno")
		p.save()
		for i in CashBook.objects.filter(AccNo=uid,AccName=pfull):
			i.AccName=FullName
			i.save()
		#print(request.POST.get('phno'),type(request.POST.get('phno')))
		return redirect(f'/view/{p.AccID}')

	d=CustomerAcc.objects.get(AccID=uid)
	return render(request,'edit.html',{'d':d,'callback':f'/view/{d.AccID}'})

def nuller(val:int):
	try:
		return int(val)
	except ValueError:
		return 0

def notesIndex(request):
	if request.user.is_anonymous:
		return redirect('/login')

	data=NoCount.objects.all().values_list('Nid','Rdate','Total').order_by('-Rdate')
	return render(request,'notesIndex.html',{'data':data})

def notesAdd(request):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method=="POST":
		p=NoCount(Rdate=dt.strptime(request.POST.get("Cdate"),'%b %d, %Y').strftime('%Y-%m-%d'),
			R2000=nuller(request.POST.get("v2k")),
			R500=nuller(request.POST.get("v5h")),
			R200=nuller(request.POST.get("v2h")),
			R100=nuller(request.POST.get("v1h")),
			R50=nuller(request.POST.get("v50")),
			RCh=nuller(request.POST.get("change")),
			Ronl=nuller(request.POST.get("online")),
			Total=nuller(request.POST.get("total")),
			Remarks=request.POST.get("remarks"),
			)
		p.save()
		return redirect('/notes/index')

	return render(request,'notesAdd.html',{'callback':'/notes/index'})

def notesEdit(request,cid):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method == 'POST':
		ed=NoCount.objects.get(Nid=cid)
		ed.R2000=nuller(request.POST.get("v2k"))
		ed.R500=nuller(request.POST.get("v5h"))
		ed.R200=nuller(request.POST.get("v2h"))
		ed.R100=nuller(request.POST.get("v1h"))
		ed.R50=nuller(request.POST.get("v50"))
		ed.RCh=nuller(request.POST.get("change"))
		ed.Ronl=nuller(request.POST.get("online"))
		ed.Total=nuller(request.POST.get("total"))
		ed.Remarks=request.POST.get("remarks")
		ed.save()
		return redirect('/notes/index')


	data=NoCount.objects.get(Nid=cid)
	multipl={'R2000':data.R2000*2000,
		     'R500':data.R500*500,
			 'R200':data.R200*200,
			 'R100':data.R100*100,
			 'R50':data.R50*50,
			}
	return render(request,'notesEdit.html',{'data':data,'valtl':multipl,'callback':'/notes/index'})

def notesDelete(request, cid):
	if request.user.is_anonymous:
		return redirect('/login')

	obj=NoCount.objects.get(Nid=cid)
	obj.delete()
	return redirect('/notes/index')

def notesView(request, cid):
	if request.user.is_anonymous:
		return redirect('/login')

	data=NoCount.objects.get(Nid=cid)
	multipl={'R2000':data.R2000*2000,
		     'R500':data.R500*500,
			 'R200':data.R200*200,
			 'R100':data.R100*100,
			 'R50':data.R50*50,
			}
	print(data.Remarks)
	return render(request,'notesView.html',{'data':data,'valtl':multipl,'callback':'/notes/index'})

