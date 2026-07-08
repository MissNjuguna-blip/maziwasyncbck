from django.urls import path
from collector import views

urlpatterns = [
    path('milk_collections/add/', views.AddMilkCollection),
    path('collections/my',views.MyCollections.as_view()),
    path('dashboard/',views.PorterDashboard)
]