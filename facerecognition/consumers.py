import json
import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from facerecognition.ai_models.recognize import encode_faces, detect_

# Encode all faces at startup
sfr = encode_faces('media/faces')

async def recognize_person_channel(frame, type):
    # Await the asynchronous detect_ function
    frame, face_names = await detect_(sfr, img=frame, type=type)
    return frame, face_names


class EnterCameraVideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Enter WebSocket connection accepted")

    async def disconnect(self, close_code):
        print("Enter WebSocket connection closed:", close_code)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Decode the incoming frame into an image
            nparr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the frame
            frame, persons = await recognize_person_channel(frame, 'enter')
            image = None
            
            if persons:
                image = "media/simu/house_imageON.jpg"
                # if self.TRIGGER else "media/simu/house_imageOFF.jpg"

            response = {
                "image": image,
                "faces": len(persons),
                "persons": persons
            }

            await self.send(text_data=json.dumps(response))
            
class ExitCameraVideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Exist WebSocket connection accepted")

    async def disconnect(self, close_code):
        print("Exist WebSocket connection closed:", close_code)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Decode the incoming frame into an image
            nparr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the frame
            frame, persons = await recognize_person_channel(frame, 'exit')
            image = None
            
            if persons:
                image = "media/simu/house_imageON.jpg"
                # if self.TRIGGER else "media/simu/house_imageOFF.jpg"

            response = {
                "image": image,
                "faces": len(persons),
                "persons": persons
            }

            await self.send(text_data=json.dumps(response))