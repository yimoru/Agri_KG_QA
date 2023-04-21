from django.conf.urls import url
from django.urls import path

from . import index
from . import _404_view

from . import view_qa

urlpatterns = [
    url(r'^$', index.index_view),
    # url(r'^404', _404_view._404_),
    path('qa', view_qa.index),
    path('qa/<page_id>/', view_qa.qa, name='qa'),
]
