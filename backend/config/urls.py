from django.contrib import admin
from django.urls import path
from exams import views
urlpatterns=[path('admin/',admin.site.urls),path('api/health/',views.health),path('api/session/',views.session),path('api/register/',views.register),path('api/login/',views.sign_in),path('api/logout/',views.sign_out),path('api/catalog/',views.catalog),path('api/attempts/',views.attempts),path('api/attempts/<uuid:pk>/',views.attempt),path('api/attempts/<uuid:pk>/submit/',views.submit)]
