from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('create/', views.budget_create, name='budget_create'),
    path('<int:pk>/', views.budget_detail, name='budget_detail'),
    path('<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    path('alerts/', views.budget_alerts, name='budget_alerts'),
    path('alerts/<int:pk>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
]