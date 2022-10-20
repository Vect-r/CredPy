from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout,authenticate,login
from django.conf import settings
from django.template.loader import get_template, render_to_string
from django.contrib.staticfiles import finders
from django.http import FileResponse,HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime as dt
from .models import CustomerAcc
from .models import CashBook
from .models import LastBalance
from .genpdf import *
from django.core import serializers
from json import dumps
import os
import io
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
			return render(request,'login.html',context={'stat':'Error: Username or Password may be incorrect'})
	
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
		data = CustomerAcc.objects.filter(FullName__icontains=url_parameter).values_list('AccID','FullName')
		k=[LastBalance.objects.get(Account=i[0]) for i in data]
		accounts=zip(data,k)
	else:
		accounts=zip(CustomerAcc.objects.all().values_list('AccID','FullName'),LastBalance.objects.all())

	ctx["accounts"] = accounts
	does_req_accept_json = request.accepts("application/json")
	is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json

	if is_ajax_request:
		html = render_to_string(template_name="index-replace.html", context={"accounts": accounts})
		data_dict = {"html_from_view": html}
		return JsonResponse(data=data_dict, safe=False)

	#updateBalanceAll()
	data=CustomerAcc.objects.values_list('AccID','FullName')
	return render(request,'index.html',context=ctx)

def updateBalanceAll():
	p=fetchall()
	for i in p.keys():
		try:
			try:
				bal=p[i][-1]
			except IndexError:
				bal="0"
			g=LastBalance.objects.get(Account=CustomerAcc.objects.get(AccID=i))
			g.Balance=bal
			g.save()
		except LastBalance.DoesNotExist:
			try:
				bal=p[i][-1]
			except IndexError:
				bal="0"
			g=LastBalance(Account=CustomerAcc.objects.get(AccID=i),Balance=bal)
			g.save()

def updateBalanceQuery(accid):
	i=accid
	p=fetchBalance(CashBook.objects.filter(AccNo=i))
	try:
		try:
			bal=p[-1]
		except IndexError:
			bal="0"
		print('Update Bal: ',bal)
		g=LastBalance.objects.get(Account=CustomerAcc.objects.get(AccID=i))
		g.Balance=bal
		g.save()
	except LastBalance.DoesNotExist:
		try:
			bal=p[-1]
		except IndexError:
			bal="0"
		print('Update Bal: ',bal)
		g=LastBalance(Account=CustomerAcc.objects.get(AccID=i),Balance=bal)
		g.save()


def about(request):
	return render(request,'about.html')

def cdate():
	return dt.now().strftime("%Y-%m-%d")

def cdatefrmt():
	return dt.now().strftime("%d.%m.%Y")	
	
def ctime():
	return dt.now().strftime('%H:%m:%S')

def addTran(request,uid):
	if request.method=="POST":
		print('OK!!!')

	if request.method == "POST":
		tranid=lastidINC()
		date=request.POST.get("Cdate")
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

	return render(request,'addTran.html',{'cdate':cdate(),'name':getname(uid),'id':uid})

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

		

def lastidINC():
	try:
		p=int(CashBook.objects.last().TranID)+1
	except:
		p=1

	return p

def getname(uid):
	return CustomerAcc.objects.get(AccID=uid).FullName

def viewAccount(request,uid,name):
	if request.user.is_anonymous:
		return redirect('/login')

	data=CustomerAcc.objects.get(AccID=uid,FullName=name)
	return render(request,'viewCustomer.html',{'data':data})

def data2json(uid,name):
	p={}
	for i in CashBook.objects.filter(AccNo=uid,AccName=name):
		p[i.TranID]={'TranID':i.TranID,
			  		 'DrAmnt':i.DrAmnt,
			  		 'CrAmnt':i.CrAmnt,
			  		 'Desc':i.Desc,
			  		 'Date':i.Date.strftime("%Y-%m-%d")}
	return p

def view(request,uid):
	if request.user.is_anonymous:
		return redirect('/login')
		
	data=CashBook.objects.filter(AccNo=uid)
	name=CustomerAcc.objects.get(AccID=uid).FullName
	datajson = dumps(data2json(uid,name))
	drttl=sum([i.DrAmnt  for i in data])
	crttl=sum([i.CrAmnt  for i in data])
	balance=fetchBalance(data)
	print(balance)
	return render(request,'viewTran.html',{'name':name,'id':uid,"data":zip(data,balance),'defdate':cdate(),"lastid":lastidINC(),'json':datajson,'cr':crttl,'dr':drttl})

def update(request,tid):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method=="POST":
		tid=request.POST.get("tranid")
		#print(request.POST.get('vCrAmnt'))
		if request.POST.get("vCrAmnt")=="":
			cr=0
		else:
			cr=request.POST.get('vCrAmnt')
		if request.POST.get("vDrAmnt")=="":
			dr=0
		else:
			dr=request.POST.get('vDrAmnt')
		cb=CashBook.objects.get(TranID=tid)
		cb.CrAmnt=cr
		cb.DrAmnt=dr
		cb.Desc=request.POST.get("vdesc")
		cb.Date=request.POST.get("vdate")
		cb.save()
		updateBalanceQuery(cb.AccNo.AccID)
		return redirect(f'/view/{cb.AccNo.AccID}')

	data=CashBook.objects.get(TranID=tid)
	return render(request,'editTran.html',{'data':data})

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
		search=request.GET.get("search")
		fdate=request.GET.get("sdate")
		edate=request.GET.get("edate")
		print(search,fdate,edate)

		if fdate is not None and edate=="" and search=="":
			print('if')
			d=CashBook.objects.filter(Date=fdate)
			p=retSum(d)
			return render(request,'reports.html',{'d':d,'fdate':f"value={fdate}",'dr':p['Dr.'],'cr':p['Cr.']})
		elif fdate is not None and edate is not None:
			d=CashBook.objects.filter(Date__range=[fdate,edate])
			p=retSum(d)
			return render(request,'reports.html',{'d':d,'fdate':f"value={fdate}",'edate':f"value={edate}",'dr':p["Dr."],'cr':p['Cr.']})

	#d=CashBook.objects.all().order_by("-Date")
	#d=CashBook.objects.all().order_by('-Time').reverse()
	d=CashBook.objects.all().order_by('-Time').order_by('-Date')
	dlist=[i.FullName for i in CustomerAcc.objects.all()]
	ttl=retSum(d)
	return render(request,'reports.html',{'d':d,'dlist':dlist,'dr':ttl['Dr.'],'cr':ttl['Cr.']})

def repdate(request):
	if request.method=="GET":
		search=request.GET.get('search')
		fdate=request.GET.get('sdate')
		edate=request.GET.get('edate')
		
		if fdate=="" and edate=="":
			data=CashBook.objects.all()
			fdate=cdate()
			frmt=[[i.AccName,i.Date.strftime('%d/%m/%Y'),i.DrAmnt,i.CrAmnt,i.Desc] for i in data]
			frmt.insert(0,['Name','Date', 'Debit', 'Credit', 'Description',])
			ttl=retSum(data)
			frmt.append(['','Total',ttl['Dr.'],ttl['Cr.'],''])
			filename=f"Dharmabhav_{cdatefrmt()}.pdf"	


		elif fdate is not None and edate=="" and search=="":
			data=CashBook.objects.filter(Date=fdate)
			frmt=[[i.AccName,i.Date.strftime('%d/%m/%Y'),i.DrAmnt,i.CrAmnt,i.Desc] for i in data]
			frmt.insert(0,['Name','Date', 'Debit', 'Credit', 'Description',])
			ttl=retSum(data)
			frmt.append(['','Total',ttl['Dr.'],ttl['Cr.'],''])
			filename=f"Dharmabhav_{fdate}.pdf"
		
		elif fdate is not None and edate is not None:
			data=CashBook.objects.filter(Date__range=[fdate,edate])
			frmt=[[i.AccName,i.Date.strftime('%d/%m/%Y'),i.DrAmnt,i.CrAmnt,i.Desc] for i in data]
			frmt.insert(0,['Name','Date', 'Debit', 'Credit', 'Description',])
			ttl=retSum(data)
			frmt.append(['','Total',ttl['Dr.'],ttl['Cr.'],''])
			filename=f"Dharmabhav_{fdate}_{edate}.pdf"
	
	print(frmt)	
	buf=io.BytesIO()
	pdf=GenReport(buf)
	pdf.Head('Dharmabhav')
	if fdate and edate=="":
		pdf.singledate(fdate)
	else:
		pdf.daterange(fdate,edate)
	pdf.dwTable(frmt)
	pdf.build()
	buf.seek(0)
	return FileResponse(buf,as_attachment=True,filename=filename)
	

def delete(request,tranid):
	if request.user.is_anonymous:
		return redirect('/login')
	else:
		print("del True")
		c=CashBook.objects.get(TranID=tranid)
		no=c.AccNo.AccID
		name=c.AccName
		c.delete()
		updateBalanceQuery(no)
		return redirect(f'/view/{no}')

'''
def genPDF(request,accid):
	template_path = 'genpdf.html'
	p=CashBook.objects.filter(AccNo=accid)
	name=p[0].AccName
	balance=fetchBalance(p)
	drttl=sum([i.DrAmnt  for i in p])
	crttl=sum([i.CrAmnt  for i in p])
	context={'data':zip(p,balance),
			'dr':drttl,
			'cr':crttl}
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename="{name}.pdf"'
	# find the template and render it.
	template = get_template(template_path)
	html = template.render(context)

	# create a pdf
	pisa_status = pisa.CreatePDF(
		html, dest=response, link_callback=link_callback)
		# if error then show some funny view
	if pisa_status.err:
		return HttpResponse('We had some errors <pre>' + html + '</pre>')

	return response
	#return render(request,'genpdf.html',)
'''

def genPDF(request,accid):
	data=CashBook.objects.filter(AccNo=accid)
	name=data[0].AccName
	balance=fetchBalance(data)
	frmt=[[i.Date.strftime('%d/%m/%Y'),i.DrAmnt,i.CrAmnt,i.Desc,j] for i,j in zip(data,balance)]
	frmt.insert(0,['Date', 'Debit', 'Credit', 'Description', 'Balance'])
	ttl=retSum(data)
	frmt.append(['Total',ttl['Dr.'],ttl['Cr.'],'',balance[-1]])
	print(frmt)
	buf=io.BytesIO()
	pdf=GenReport(buf)
	pdf.Head(name)
	pdf.singledate(cdate())
	pdf.accTable(frmt)
	pdf.build()
	buf.seek(0)
	return FileResponse(buf,as_attachment=True,filename=f'{name}.pdf')

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
	
		submit=CustomerAcc(FullName=name,Address=address,phno=phno,Email=email,DateCreated=cdate(),TimeCreated=ctime())
		submit.save()
		o=LastBalance(Account=submit,Balance='0')
		o.save()
		return redirect('/')

	return render(request,'addCustomer.html')

def deleteAccount(request,accid,name):
	if request.user.is_anonymous:
		return redirect('/login')

	print(accid)
	c=CustomerAcc.objects.get(AccID=accid,FullName=name)
	c.delete()
	return redirect('/')


def editAccount(request,uid,name):
	if request.user.is_anonymous:
		return redirect('/login')

	if request.method=="POST":
		accid=request.POST.get("accid")
		FullName=request.POST.get("name")
		p=CustomerAcc.objects.get(AccID=accid)
		pfull=p.FullName
		p.FullName=FullName
		p.Address=request.POST.get("address")
		p.Email=request.POST.get("e-mail")
		if request.POST.get("phno")=="None":
			p.phno=0
		else:
			p.phno=request.POST.get("phno")
		p.save()
		for i in CashBook.objects.filter(AccNo=accid,AccName=pfull):
			i.AccName=FullName
			i.save()
		print(request.POST.get('phno'),type(request.POST.get('phno')))
		return redirect(f'/view/{p.AccID}')

	d=CustomerAcc.objects.get(AccID=uid,FullName=name)
	return render(request,'edit.html',{'d':d})