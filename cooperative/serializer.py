from rest_framework import serializers
from core.models import FarmerProfile, Notice,PorterProfile,FeedBack,MilkCollection

# admin/cooperative farmer account
class FarmerSerializer (serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = '__all__'

class PorterSerializer (serializers.ModelSerializer):
    class Meta:
        model = PorterProfile
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = ['id','title','description','created_at','update_at']
        raed_only_fields=['status','created_at','update_at']

class MilkCollectorSerializer(serializers.ModelSerializer):
    farmer_name= serializers.SerializerMethodField()
    national_id= serializers.CharField(
        source='farmer.national_id',
        read_only=True
    )

    class Meta:
        model= MilkCollection
        fields = [
            'id',
            'national_id',
            'farmer_name',
            'liters',
            'session',
            'total_amount',
            'collection_date',
        ]

    def get_farmer_name(self,obj):
        return f"{obj.farmer.first_name} {obj.farmer.last_name}"
    

# Notice
class NoticeSerializer (serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ['created_by', 'update_at']