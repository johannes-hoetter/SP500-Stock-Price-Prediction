from django.conf.urls import url
from . import views

urlpatterns = [
    url('', views.index, name='index'),
    url('go', views.go, name='go'),
]