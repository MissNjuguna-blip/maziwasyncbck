from rest_framework import serializers

from core.models import MilkCollection
from core.models import FeedBack


# serializer for the farmer milk collection showing also porter who collected the milk
class MilkCollectionSerializer(serializers.ModelSerializer):
    porter_name = serializers.SerializerMethodField()
    class Meta:
        model=MilkCollection
        fields = ['id','liters','session','price_per_liter','total_amount','collection_date','porter_name']

    def get_porter_name(self,obj):
        return f"{obj.porter.first_name} {obj.porter.last_name}"
    
# feedback serializer
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = ['id','title','description','created_at','update_at']
        raed_only_fields=['status','created_at','update_at']