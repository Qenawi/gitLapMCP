from django.urls import path
from jsonrpc.site import jsonrpc_site
from jsonrpc import views

urlpatterns = [
    path('', jsonrpc_site.dispatch, name='jsonrpc'),
    path('browse/', views.browse, name='jsonrpc-browse'),
]
