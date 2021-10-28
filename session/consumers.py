from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from django.contrib.auth.models import AnonymousUser

from session.models import Session

class TestConsumer(WebsocketConsumer):
    
    async def connect(self):
        # print(self.scope)

        session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_name = "session_{session_id}"
        self.room_group_name = "session_group_{session_id}"
        session = Session.objects.filter(id=session_id)
        if not session.exists():
            await self.close()
            return
        
        if type(self.scope["user"])==AnonymousUser:
            await self.close()
            return
        self.accept()
        # self.send(text_data=json.dumps({'status':'connection hogya'}))
    
    def receive(self, text_data=None, bytes_data=None):
        print(text_data)
        self.send(text_data=json.dumps({'status':'receive hogya'}))
        return super().receive(text_data=text_data, bytes_data=bytes_data)
    
    def send(self, text_data=None, bytes_data=None, close=False):
        return super().send(text_data=text_data, bytes_data=bytes_data, close=close)
    
    def disconnect(self, code):
        print("disconnect hogya")
        return super().disconnect(code)