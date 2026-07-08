from datetime import timedelta
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from core.models import FarmerProfile, MilkCollection, PorterProfile
from rest_framework.response import Response
from rest_framework import generics
from collector.serializer import MilkCollectorSerializer, RecentCollectionSerializer
from django.utils import timezone
from django.db.models import Sum

# Create your views here.

# Porter Dashboard
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def PorterDashboard(request):
    # get Logged in porter user
    try:
        porter=request.user.porter_profile
    except PorterProfile.DoesNotExist:
        return Response ({"error":"Only Porters can access this dashboard"})
    
    # time settings
    today= timezone.now().date()
    week_start= today-timedelta(days=7)
    month_start=today.replace(day=1)

    # Todays Collections
    today_collections=MilkCollection.objects.filter(porter=porter,collection_date=today)
    total_collection_today=today_collections.count()
    total_liters_today=today_collections.aggregate(total=Sum('liters'))["total"] or 0
    total_amount_today=today_collections.aggregate(total=Sum('total_amount'))['total']or 0

    # weekly/monthly
    weekly_collections=MilkCollection.objects.filter(porter=porter,collection_date__gte=week_start)
    total_liters_week=weekly_collections.aggregate(total=Sum('liters'))["total"] or 0

    monthly_collections=MilkCollection.objects.filter(porter=porter,collection_date__gte=month_start)
    total_liters_month=monthly_collections.aggregate(total=Sum('liters'))["total"] or 0

    # current 5 collections
    last_collections = MilkCollection.objects.filter(porter=porter).order_by("created_at")[:5]

    # serialize the multiple milk collection
    last_collection_list=RecentCollectionSerializer(last_collections,many=True).data

    response_data = {
        'date':today,
        'assigned_farmers':porter.assigned_farmers.count(),
        'total_collections_today':total_collection_today,
        'total_liters_today':total_liters_today,
        'total_amount_today':total_amount_today,
        'total_liters_week':total_liters_week,
        'total_liters_month':total_liters_month,
        'last_collections':last_collection_list,
        'porter_name':f"{porter.first_name} {porter.last_name}",
        'route_name':porter.route_name,
        'employee_id':porter.employee_id,
    }
    return Response(response_data)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AddMilkCollection(request):
    # get the logged in user
    try:
        porter = request.user.porter_profile
    except PorterProfile.DoesNotExist:
        return Response({'error':'No porter account'})
       
    try:
        national_id = request.data.get("national_id")
        farmer = FarmerProfile.objects.get(national_id=national_id)
    except FarmerProfile.DoesNotExist:
        return Response({'error':'No farmer account'})
    
    collection = MilkCollection.objects.create(
        farmer=farmer,
        porter=porter,
        liters=request.data.get("liters"),
        session=request.data.get("sessions")
    )

    return Response ({
        'message':'Milk Collectionrecorded successfully',
        "collection_id":collection.id,
        "farmer":f'{farmer.first_name} {farmer.last_name}',
        "porter":f'{porter.first_name} {porter.last_name}',
        "liters":collection.liters,
    })

# view porter collections list
class MyCollections(generics.ListAPIView):
    serializer_class=MilkCollectorSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        porter=self.request.user.porter_profile
        collections=(
            MilkCollection.objects.filter(porter=porter).select_related('farmer').order_by('created_at')
        )
        return  collections