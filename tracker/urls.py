from django.urls import path
from . import views

urlpatterns = [
    path('', views.study_days_list, name='study_days_list'),
    path('analytics/data/', views.analytics_data, name='analytics_data'),
]
