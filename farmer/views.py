from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from .serializer import FeedbackSerializer, MilkCollectionSerializer
from core.models import FarmerProfile, MilkCollection,FeedBack, Notice
from django.db.models import Sum
from datetime import date
from django.utils import timezone
from rest_framework.response import Response
from cooperative.serializer import NoticeSerializer

# Create your views here.

# Farmer Dashboard
class FarmerDashboard(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        farmer=self.request.user.farmer_profile
        collection=MilkCollection.objects.filter(farmer=farmer)
        total_collection=collection.count()
        total_liters = collection.aggregate(total=Sum('liters'))['total'] or 0
        total_amount = collection.aggregate(total = Sum('total_amount'))['total'] or 0

        today_collection = collection.filter(collection_date=date.today()).aggregate(total=Sum('liters'))['total'] or 0

        monthly_liters=collection.filter(collection_date__month=timezone.now().month).aggregate(total=Sum('liters'))['total'] or 0

        monthly_earnings=collection.filter(collection_date__month=timezone.now().month).aggregate(total=Sum('total_amount'))['total'] or 0
         
        return Response ({
            "total_collections":total_collection,
            "total_liters":total_liters,
            "total_amount": total_amount,
            "monthly_earnings":monthly_earnings,
            "monthly_liters":monthly_liters
        })



class FarmerCollection(generics.ListAPIView):
    serializer_class=MilkCollectionSerializer
    permission_classes=[IsAuthenticated]

    # query set-fetch data from model in class
    def get_queryset(self):
        try:
            farmer=self.request.user.farmer_profile
        except FarmerProfile.DoesNotExist:
            raise PermissionDenied (
                "Only Farmers can access this endpoint"
            )
        collections = (
            MilkCollection.objects
            .filter(farmer=farmer)
            .select_related('porter')
            .order_by('created_at')
        ) 
        return collections
    
# feedback
class FeedbackViewset(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_class=[IsAuthenticated]
    def get_queryset(self):
        try:
            farmer=self.request.user.farmer_profile
        except:
            raise PermissionDenied("Only farmers can access this end point")
        
        feedback=(
            FeedBack.objects
            .filter(farmer=farmer)
            .order_by('created_at')
        )

        return feedback
    
    # post m
    def perform_create(self,serializer):
        try:
            farmer=self.request.user.farmer_profile
        except:
            raise PermissionDenied("Only farmers can access this end point")
        
        serializer.save(farmer=farmer)

    

class FarmerViewSet(generics.ListAPIView):
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        notices = (
            Notice.objects.filter(target__in = ['ALL','FARMERS'])
            .order_by('created_at')
        )
        return notices