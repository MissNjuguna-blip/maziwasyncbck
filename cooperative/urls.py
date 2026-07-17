from django.urls import path,include
from rest_framework.routers import DefaultRouter
from cooperative import views

router= DefaultRouter()
router.register('farmer', views.FarmerViewSet, basename='farmers')
router.register('porter', views.PorterViewSet, basename='porters')
router.register('notice', views.NoticeViewSet, basename='notice')
urlpatterns = [
    path ('',include(router.urls)),
    path('feedback', views.ViewFeedBack.as_view())
]