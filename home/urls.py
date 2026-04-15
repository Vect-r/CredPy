from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('',views.index,name="home"),
    path('about',views.about,name='about'),
    path('addAccount',views.addAccount,name='addAccount'),
    path('generate/<int:uid>',views.genPDF,name='genpdf'),
    path('view/<int:uid>',views.view,name="view"),
    path('addTran/<int:uid>',views.addTran,name="addT"),
    path('update/<int:tid>',views.update,name="editTrns"),
    path('delete/<int:tranid>',views.delete,name="delTrns"),
    path('reports',views.reports,name="reports"),
    path('editAccount/<int:uid>',views.editAccount,name="editAcc"),
    path('viewAccount/<int:uid>',views.viewAccount,name='viewAccount'),
    path('delAccount/<int:accid>',views.deleteAccount,name='delAcc'),
    #path('addTranapi',views.addTranAPI,name="addTranapi"),
    #path('addAccountapi',views.addAccountAPI,name="addAccountapi"),
    #path('del1op',views.bac,name="exp_bkp"),
    path('logout',views.logoutUser,name='logout'),
    path('genreportdate',views.repdate,name="repdate"),
    path('login',views.loginUser,name='login'),
    path('notes/index',views.notesIndex,name="notesIndex"),
    path('notes/add',views.notesAdd,name="notesAdd"),
    path('notes/delete/<int:cid>',views.notesDelete,name='notesDelete'),
    path('notes/edit/<int:cid>',views.notesEdit,name="noteEdit"),
    path('notes/view/<int:cid>',views.notesView,name="noteView"),
    path('addQuick',views.addQuick,name="addQuick"),
]