from django.urls import include, path
from farmer import views
from rest_framework.routers import DefaultRouter


router=DefaultRouter()
router.register('feedback', views.FeedbackViewset,basename='feedback')
urlpatterns = [
    path('farmercollection/' ,views.FarmerCollection.as_view()),
    path('', include(router.urls))
]