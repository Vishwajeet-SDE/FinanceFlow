from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('spending-breakdown/', views.spending_breakdown, name='spending_breakdown'),
    path('financial-report/', views.financial_report, name='financial_report'),
    path('savings-goals/', views.savings_goals_list, name='savings_goals_list'),
    path('savings-goals/<int:pk>/', views.savings_goal_detail, name='savings_goal_detail'),
]