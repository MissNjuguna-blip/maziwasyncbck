from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .serializer import FeedbackSerializer, MilkCollectionSerializer
from core.models import FarmerProfile, MilkCollection,FeedBack

# Create your views here.
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

    
        