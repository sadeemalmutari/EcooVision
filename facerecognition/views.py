from django.shortcuts import render,redirect
from .models import  Person,Activity
from .models import Person
from django.shortcuts import render
from django.utils import timezone
from .models import Person, Activity, Room
# rest framework

from rest_framework import permissions ,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
import base64
from rest_framework.decorators import api_view
from django.utils import timezone
import os
import cv2
import numpy as np
import pandas as pd
from django.http import HttpResponse
from datetime import datetime

from facerecognition.ai_models.recognize import encode_faces,detect_,encode_face
from .serializers import  PersonSerializer,ActivitySerializer,RoomSerializer
from rest_framework import permissions, status
# get_object_or_404
from django.shortcuts import get_object_or_404


save_directory = 'media/'


def add_person_page(request):
    return render(request,'add_person.html')
@api_view(['GET'])
def _face_recognition(request):
    return render(request,'face_recognition.html')

def all_acrivites_page(request):
    activities = Activity.objects.all()
    serializer = ActivitySerializer(activities, many=True)
    
    return render(request,'all_activities.html',{'person_activities':serializer.data})

def export_activities_to_excel(request):
    # Query all activities and related data
    activities = Activity.objects.select_related('person').all()

    # Create a DataFrame from the activities data
    data = []
    for activity in activities:
        data.append({
            'Name': activity.person.name,
            'About': activity.person.about,
            'Enter Date': activity.enter_date.strftime('%Y-%m-%d %I:%M %p') if activity.enter_date else '',
            'Exit Date': activity.exit_date.strftime('%Y-%m-%d %I:%M %p') if activity.exit_date else '',
            'Actual Enter Date': activity.actual_enter_date.strftime('%Y-%m-%d %I:%M %p') if activity.actual_enter_date else '',
            'Actual Exit Date': activity.actual_exit_date.strftime('%Y-%m-%d %I:%M %p') if activity.actual_exit_date else '',
            'Action': activity.action,
            'Image': activity.image.url if activity.image else 'No Image'
        })

    # Create pandas DataFrame
    df = pd.DataFrame(data)

    # Create a response with the Excel file as the content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="activities.xlsx"'

    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Activities')

    return response

# get all rooms
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)
# update_room
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_room(request, id):
    try:
        room = get_object_or_404(Room, id=id)
        if request.content_type == 'application/json':
            data = request.data
        else:
            data = request.POST
        room.light_status = data.get('light_status', room.light_status)
        room.save()
        return Response({'details': 'Room updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# get room by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_room_by_id(request, id):
    room = get_object_or_404(Room, id=id)
    serializer = RoomSerializer(room)
    return Response(serializer.data)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_person(request):
    if request.content_type == 'application/json':
        data = request.data
    else:
        data = request.POST
    if request.FILES:
        img = request.FILES['image']
        print(img)
    name = data.get('name')
    about = data.get('about')
    enter_date=data.get('enter_date')
    exit_date=data.get('exit_date')
    room_number=data.get('room_number')
    # Convert naive datetime to timezone-aware datetime
    # if enter_date:
    #    enter_date = timezone.make_aware(datetime.strptime(enter_date, "%Y-%m-%dT%H:%M"))
    # if exit_date:
    #     exit_date = timezone.make_aware(datetime.strptime(exit_date, "%Y-%m-%dT%H:%M"))

    room=Room.objects.get(id=room_number)
    person = Person.objects.create(
        name=name,
        about=about,
        enter_date=enter_date,
        room=room,
        exit_date=exit_date
    )
    person.image = img
    person.save()
    encoding = encode_face(person.image.path)
    if encoding is not None:
        person.face_encoding = str(encoding.tolist())
        person.save()
    else:
        person.delete()
        return Response({'details': 'No Faces Detected'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'details': 'Person added successfully'}, status=status.HTTP_201_CREATED)




@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_person(request, id):  # `id` is now explicitly passed as a URL parameter
    try:
        # Fetch the person instance or return a 404 if not found
        person = get_object_or_404(Person, id=id)

        # Handle incoming data
        if request.content_type == 'application/json':
            data = request.data
        else:
            data = request.POST

        # Optional file handling
        img = request.FILES.get('image', None)

        # Update fields
        person.name = data.get('name', person.name)  # Use the existing value if not provided
        person.about = data.get('about', person.about)
        person.enter_date = data.get('enter_date', person.enter_date)
        person.exit_date = data.get('exit_date', person.exit_date)  # Fixed `exist_date` typo
        if img:
            person.image = img

        person.save()

        # Perform face encoding if an image is provided
        if img:
            encoding = encode_face(person.image.path)
            if encoding is not None:
                person.face_encoding = str(encoding.tolist())
                person.save()
            else:
                # Delete the person if no face detected
                person.delete()
                return Response({'details': 'No Faces Detected'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'details': 'Person updated successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# get all Activity
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_activity(request):
    activities = Activity.objects.all()
    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)