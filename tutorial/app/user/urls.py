from django.contrib import admin
from django.urls import path, re_path
from .views import UserRudAPIView, UserCreateAPIView

urlpatterns = [
    re_path(r'^(?P<pk>\d+)/$', UserRudAPIView.as_view()),
    path('', UserCreateAPIView.as_view()),

]
