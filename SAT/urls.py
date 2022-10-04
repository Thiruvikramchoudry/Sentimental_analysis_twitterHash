from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('analysis_page',views.analysis_page,name="analysis_page"),
]