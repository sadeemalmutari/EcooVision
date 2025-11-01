import cv2
from matplotlib import pyplot as plt
from .simple_facerec import SimpleFacerec #for django
from django.utils import timezone
from asgiref.sync import sync_to_async
# Encode faces from a folder
import face_recognition

def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        return encodings[0]
    else:
        return None

def encode_faces(path='images/faces'):
    """
    this function encodes faces from a folder and returns the SimpleFacerec object 
    with the faces encoded in it
    """
    
    sfr = SimpleFacerec()
    
    sfr.load_encoding_images(path)
    print("faces encoded")
    return sfr

    

async def detect_(sfr, img=None, img_path='', type='enter'):
    from facerecognition.models import Person, Room, Activity
    from django.utils import timezone
    """
    This function detects faces in an image and returns the image with the faces detected and the names of the detected faces
    """
    if img is not None:
        frame = img
    elif img_path:
        img = cv2.imread(img_path)
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect Faces
    face_locations, face_names = sfr.detect_known_faces(frame)
    persons = []

    for face_loc, name in zip(face_locations, face_names):
        # try:
        print('Detected person ID:', name)

        # Wrap ORM calls in sync_to_async
        person = await sync_to_async(Person.objects.get)(pk=int(name))
        print('Person:', person)

        room = await sync_to_async(lambda: person.room)()
        # room = await sync_to_async(Room.objects.get)(pk=person.room)
        print('Room:', room.name)
        print('type:', type)

        

        # Create activity record
        if type == 'enter':
            await sync_to_async(Activity.objects.create)(
                person=person,
                room=room,
                date=timezone.now(),
                enter_date=person.enter_date,
                exit_date=person.exit_date,
                action='enter',
                actual_enter_date=timezone.now(),
                actual_exit_date=None,
            )
        else:
            await sync_to_async(Activity.objects.create)(
                person=person,
                room=room,
                date=timezone.now(),
                enter_date=person.enter_date,
                exit_date=person.exit_date,
                action='exit',
                actual_enter_date=None,
                actual_exit_date=timezone.now(),
            )
        # Update light status
        room.light_status = True if type == 'enter' else False
        await sync_to_async(room.save)()
        print('Light status:', room.light_status)
        
        persons.append({'name': person.name, "room": room.id})
        print('Persons:', persons)

        # except Exception as e:
        #     print(f"Error processing person {name}:", e)
        #     pass

        # Draw on the frame
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
        cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 200), 4)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

    return frame, persons