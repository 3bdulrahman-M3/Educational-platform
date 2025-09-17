from rest_framework import serializers
from .models import LiveSession

class LiveSessionSerializer(serializers.ModelSerializer):
    host = serializers.SerializerMethodField()
    created_by = serializers.ReadOnlyField(source='created_by.id')  
    end_date = serializers.DateTimeField(required=False, allow_null=True) 

    class Meta:
        model = LiveSession
        fields = ['id', 'title', 'created_by', 'host', 'created_at', 'room_name', 'end_date']

    def get_host(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()