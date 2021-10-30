import json
from typing import Text
import requests
from channels.generic.websocket import AsyncWebsocketConsumer

from django.db.models.query_utils import Q
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError

from rest_framework import serializers

from session.models import Session
from pokerboard.models import Pokerboard
from pokerboard import constants
from session.serializers import MethodSerializer
from pokerplanner import settings
from session.utils import checkEstimateValue

class TestConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        """
        Runs when a request to make a connection is received.
        """
        session_id = self.scope['url_route']['kwargs']['session_id']
        session = Session.objects.filter(id=session_id,status=Session.ONGOING)
        #Session does not exist or session is not ongoing.
        if not session.exists():
            await self.close()
            return
        
        #User is anonymous 
        if type(self.scope["user"])==AnonymousUser:
            await self.close()
            return
        
        #Session is ongoing and is valid but user is not part of pokerboard.
        pokerboard = Pokerboard.objects.filter(Q(manager=self.scope['user']) | 
                Q(invite__user=self.scope['user'],invite__status=constants.ACCEPTED)).distinct()
        
        session_pokerboard = pokerboard.filter(id=session.first().pokerboard.id) 
        if not session_pokerboard:
            await self.close()
            return
            
        self.room_name = session.first().title
        self.room_group_name = 'session_%s' % self.room_name
        self.personal_group = 'user_%s' % self.scope['user'].id
        print(f'personal group {self.personal_group}')
        #Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.personal_group,
            self.channel_name
        )
        
        all_members = getattr(self.channel_layer,self.room_group_name,[])
        all_members.append(self.scope['user'])
        setattr(self.channel_layer,self.room_group_name,all_members)
        
        await self.accept()
        self.pokerboard_manager = pokerboard.first().manager
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast',
                'message': f"{self.scope['user']} has joined the session {self.room_name}"
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
                'message': f"{self.scope['user']} has left the session {self.room_name}."
            }
        )
    
    async def broadcast(self, event):
        """
        Runs to send the message to all the user.
        """
        message = event["message"]
        await self.send(text_data=json.dumps(message))

    async def receive(self, text_data=None, bytes_data=None):

        try:
            data_json = json.loads(text_data)
            serializer = MethodSerializer(data=data_json)
            serializer.is_valid(raise_exception=True)
            method_name = serializer.validated_data["method_name"]
            method_value = serializer.validated_data["method_value"]
            fn_name = getattr(self,method_name)
            await fn_name({
                'type':method_name,
                'message':method_value
            })
        except serializers.ValidationError as e:
            await self.send(text_data=json.dumps({"error":"Something went wrong."}))
        except json.decoder.JSONDecodeError as e:
            await self.send(text_data=json.dumps({"error":"invalid json input"}))

    
    async def estimate(self, event):
        """
        Estimates tickets by user and manager and also update in jira.
        """
        session = Session.objects.get(id=self.scope['url_route']['kwargs']['session_id'])
        deck_type = session.pokerboard.estimation_type
        try:
            ticket_key = event["message"]["ticket_key"]
            estimate = event["message"]["estimate"]
            if not checkEstimateValue(deck_type,estimate):
                raise ValidationError("Invalid estimate value")
            if self.scope['user'] == self.pokerboard_manager:
                jira = settings.JIRA
                set_estimate = {'customfield_10016':estimate}
                jira.update_issue_field(ticket_key, set_estimate)     
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'message': f"Final Estimate on ticket {ticket_key} is {estimate}"
                    }
                )
            else:
                manager_room_name = 'user_%s' % self.pokerboard_manager.id
                await self.channel_layer.group_send(
                    manager_room_name,
                    {
                        'type': 'message.manager',
                        "username": self.scope['user'].email,
                        'ticket_key':ticket_key,
                        'message': estimate
                    }
                )
        except ValidationError as e:
            await self.send(text_data=json.dumps({"error":f'{e}'}))
        except KeyError as e:
            await self.send(text_data=json.dumps({"error":f'{e}'}))
        except requests.exceptions.HTTPError as e:
            await self.send(text_data=json.dumps({"error":f'{e}'}))        

    async def message_manager(self, event):
        """
        Send user estimate to manager
        """
        await self.send(
            text_data=json.dumps
            ({
                "username": event["username"],
                "ticket": event["ticket_key"],
                "estimate": event["message"],
            }),
        )

    def send(self, text_data=None, bytes_data=None, close=False):
        return super().send(text_data=text_data, bytes_data=bytes_data, close=close)

    
