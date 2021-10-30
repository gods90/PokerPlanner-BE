from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from django.contrib.auth.models import AnonymousUser
from django.db.models import manager
from django.db.models.query_utils import Q
from pokerboard import constants
from rest_framework import serializers
from pokerboard.models import Pokerboard

from session.models import Session
from session.serializers import MethodSerializer
from user.serializer.serializers import UserSerializer

class TestConsumer(AsyncJsonWebsocketConsumer):
    
    async def connect(self):
        """
        Runs when a request to make a connection is received.
        """
        session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_name = session_id
        self.room_group_name = 'session_%s' % self.room_name
        session = Session.objects.filter(id=session_id)
        
        #Session does not exist.
        if not session.exists():
            await self.close()
            return
        
        #User is anonymous or session is not ongoing
        if type(self.scope["user"])==AnonymousUser or session.first().status != Session.ONGOING:
            await self.close()
            return
        
        #Session is ongoing and is valid but user is not part of pokerboard.
        pokerboard = Pokerboard.objects.filter(Q(manager=self.scope['user']) | 
                Q(invite__user=self.scope['user'],invite__status=constants.ACCEPTED)).distinct()
        
        session_pokerboard = pokerboard.filter(id=session.first().pokerboard.id) 
        if not session_pokerboard:
            await self.close()
            return
            
        #Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        all_members = getattr(self.channel_layer,self.room_group_name,[])
        all_members.append(self.scope['user'])
        setattr(self.channel_layer,self.room_group_name,all_members)
        
        await self.accept()
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast',
                'message': f"{self.scope['user']} has joined the session."
            }
        )
        
    async def disconnect(self, code):
        """
        Runs when connection is closed.
        """
        all_members = getattr(self.channel_layer,self.room_group_name,[])
        all_members.remove(self.scope['user'])
        setattr(self.channel_layer,self.room_group_name,all_members)
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast',
                'message': f"{self.scope['user']} has left the session."
            }
        )
    
    async def broadcast(self, event):
        """
        Runs to send the message to all the user.
        """
        message = event["message"]
        await self.send(text_data=json.dumps(message))
    
    async def start_game(self, event):
        """
        Starts the game and get all the user in the session.
        """
        all_members = getattr(self.channel_layer,self.room_group_name,[])
        serializer = UserSerializer(all_members,many=True)
        return{
            "type":event["type"],
            "message":serializer.data
        }
        
    async def receive(self, text_data=None, bytes_data=None):
        try:
            data_json = json.loads(text_data)
            serializer = MethodSerializer(data=data_json)
            serializer.is_valid(raise_exception=True)
            method_name = serializer.validated_data["method_name"]
            method_value = serializer.validated_data["method_value"]
            fn_name = getattr(self,method_name)
            result = await fn_name({
                'type':method_name,
                'message':method_value
            })
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast',
                    'message': result["message"]
                }
            )
        except serializers.ValidationError as e:
            await self.send(text_data=json.dumps({"error":"Something went wrong."}))
                
    # def send(self, text_data=None, bytes_data=None, close=False):
    #     return super().send(text_data=text_data, bytes_data=bytes_data, close=close)

