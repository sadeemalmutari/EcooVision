from django.contrib import admin
from rest_framework import serializers
from django.utils import timezone
from .models import Activity, Person ,Room

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = 'id', 'name', 'about', 'image', 'enter_date', 'exit_date', 'room', 'in_house'
class RoomSerializer(serializers.ModelSerializer):
    # just return first owner
    owner = PersonSerializer(many=True,read_only=True) 
    class Meta:
        model = Room
        fields = '__all__'
    


class ActivitySerializer(serializers.ModelSerializer):
    person = PersonSerializer()  # Nested serializer to include person details
    
    # Use SerializerMethodField to display formatted datetime fields
    enter_date = serializers.SerializerMethodField()
    exit_date = serializers.SerializerMethodField()
    actual_enter_date = serializers.SerializerMethodField()
    actual_exit_date = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()  # For formatted image URL if needed

    class Meta:
        model = Activity
        fields = [
            'person',
            'enter_date',
            'exit_date',
            'actual_enter_date',
            'actual_exit_date',
            'image',
            'image_url',
            'action'
        ]

    # Helper to format the enter_date to 12-hour format
    def get_enter_date(self, obj):
        if obj.enter_date:
            return obj.enter_date.strftime('%I:%M %p')  # Format: 12:00 PM
        return None

    # Helper to format the exit_date to 12-hour format
    def get_exit_date(self, obj):
        if obj.exit_date:
            return obj.exit_date.strftime('%I:%M %p')
        return None

    # Helper to format the actual_enter_date to local timezone with date and 12-hour format
    def get_actual_enter_date(self, obj):
        if obj.actual_enter_date:
            return timezone.localtime(obj.actual_enter_date).strftime('%Y-%m-%d %I:%M %p')
        return None

    # Helper to format the actual_exit_date to local timezone with date and 12-hour format
    def get_actual_exit_date(self, obj):
        if obj.actual_exit_date:
            return timezone.localtime(obj.actual_exit_date).strftime('%Y-%m-%d %I:%M %p')
        return None

    # Helper to get the absolute URL for the image field
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None