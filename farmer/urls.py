from django.urls import include, path
from farmer import views
from rest_framework.routers import DefaultRouter


router=DefaultRouter()
router.register('feedback', views.FeedbackViewset,basename='feedback')
urlpatterns = [
    path('farmercollection/' ,views.FarmerCollection.as_view()),
    path('', include(router.urls)),
    path('dashboard/', views.FarmerDashboard.as_view()),
    path('notices',views.FarmerViewSet.as_view()), 
    path('predict/',views.PredictDiseases), 
]