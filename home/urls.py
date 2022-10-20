from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('',views.index,name="home"),
    path('about',views.about,name='about'),
    path('addAccount',views.addAccount,name='addAccount'),
    path('generate/<int:accid>',views.genPDF,name='genpdf'),
    path('view/<int:uid>',views.view,name="view"),
    path('addTran/<int:uid>',views.addTran,name="addT"),
    path('update/<int:tid>',views.update,name="editTrns"),
    path('delete/<int:tranid>',views.delete,name="delTrns"),
    path('reports',views.reports,name="reports"),
    path('editAccount/<int:uid>/<str:name>',views.editAccount,name="editAcc"),
    path('viewAccount/<int:uid>/<str:name>',views.viewAccount,name='viewAccount'),
    path('delAccount/<int:accid>/<str:name>',views.deleteAccount,name='delAcc'),
    path('addTranapi',views.addTranAPI,name="addTranapi"),
    path('addAccountapi',views.addAccountAPI,name="addAccountapi"),
    path('logout',views.logoutUser,name='logout'),
    path('genreportdate',views.repdate,name="repdate"),
    path('login',views.loginUser,name='login')
]