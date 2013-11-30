# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from likes import views 

urlpatterns = patterns('',
    url(r'^(?P<object_pk>\d+)-(?P<app_label>\w+)-(?P<model>\w+)-(?P<likes>\d)$', views.like_item, name='likes_like_item'),
    url(r'^likers/(?P<object_pk>\d+)-(?P<app_label>\w+)-(?P<model>\w+)-(?P<likes>\d)$', views.get_list_likers, name='likes_likers'),
    url(r'^count/(?P<object_pk>\d+)-(?P<app_label>\w+)-(?P<model>\w+)-(?P<likes>\d)$', views.get_like_count, name='likes_count'),
)
