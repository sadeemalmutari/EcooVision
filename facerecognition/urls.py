from django.urls import path
from . import views

urlpatterns=[
    path('person/add',views.add_person_page, name='add_person_page'),
    path('add_person/',views.add_person, name='add_person'),
    path('face_recognition/',views._face_recognition, name='face_recognition'),
    path('export-activities/', views.export_activities_to_excel, name='export_activities_to_excel'),
    path('update-person/<int:id>/', views.update_person, name='update-person'),
    path('activities/', views.all_acrivites_page, name='all-activities-page'),
    path('all-activities/', views.get_all_activity, name='all-activities'),
    path('rooms/', views.get_all_rooms, name='all-rooms'),
    path('room/<int:id>/update/', views.update_room, name='update-room'),
    path('room/<int:id>/', views.get_room_by_id, name='get-room'),
    
]