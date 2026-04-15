from django.db import models
from datetime import datetime

# Create your models here.
class CustomerAcc(models.Model):
	AccID=models.AutoField(primary_key=True)
	FullName = models.TextField(null=False)
	Address = models.TextField(null=True,blank=True)
	phno = models.IntegerField(null=True,blank=True)
	Email = models.EmailField(null=True,blank=True)
	LastBalance=models.TextField(null=True)
	DateCreated = models.DateField()
	TimeCreated = models.TimeField()

class CashBook(models.Model):
	TranID=models.IntegerField(primary_key=True)
	AccNo=models.ForeignKey(CustomerAcc,on_delete=models.CASCADE)
	AccName=models.CharField(max_length=20)
	DrAmnt=models.IntegerField()
	CrAmnt=models.IntegerField()
	Desc=models.TextField()
	Date = models.DateField(null=False)
	Time = models.TimeField(null=False)

class NoCount(models.Model):
	Nid=models.AutoField(primary_key=True)
	Rdate=models.DateField(null=False)
	R2000=models.IntegerField(null=True, blank=True)
	R500=models.IntegerField(null=True, blank=True)
	R200=models.IntegerField(null=True, blank=True)
	R100=models.IntegerField(null=True, blank=True)
	R50=models.IntegerField(null=True, blank=True)
	RCh=models.IntegerField(null=True, blank=True)
	Ronl=models.IntegerField(null=True, blank=True)
	Total=models.IntegerField(null=True, blank=True)
	Remarks=models.TextField(null=True, blank=True)	