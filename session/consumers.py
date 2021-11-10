import json
import requests
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from django.db.models.query_utils import Q
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from pokerboard import constants
from pokerboard.models import Pokerboard, Ticket
from pokerplanner import settings
from session.models import Session
from session.serializers import MethodSerializer
from session.utils import checkEstimateValue, set_user_estimates, move_ticket_to_last
from user.serializer.serializers import UserSerializer


class SessionConsumer(AsyncWebsocketConsumer):
    """
    Session Consumer for web socket connections.
    """
    async def connect(self):
        """
        Runs when a request to make a connection is received.
        """
        session_id = self.scope['url_route']['kwargs']['session_id']
        self.session = Session.objects.filter(id=session_id, status=Session.ONGOING)
        
        #Session does not exist or session is not ongoing or User is anonymous .
        if not self.session.exists() or type(self.scope['user']) == AnonymousUser:
            await self.close()
            return
        
        #Session is ongoing and is valid but user is not part of pokerboard.
        pokerboard = Pokerboard.objects.filter(
            Q(manager=self.scope['user']) 
            | Q(invite__user=self.scope['user'], 
            invite__status=constants.ACCEPTED)
        ).distinct()
        
        session_pokerboard = pokerboard.filter(id=self.session.first().pokerboard.id) 
        if not session_pokerboard:
            await self.close()
            return
            
        self.room_name = self.session.first().id
        self.room_group_name = 'session_%s' % self.room_name
        self.personal_group = 'user_%s' % self.scope['user'].id

        all_members = getattr(self.channel_layer, self.room_group_name, [])
        if self.scope['user'] in all_members:
            await self.accept()
            self.pokerboard_manager = pokerboard.first().manager
            return
        all_members.append(self.scope['user'])
        setattr(self.channel_layer, self.room_group_name, all_members)
        
        await self.accept()
        self.pokerboard_manager = pokerboard.first().manager

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast',
                'data': {
                    'context': 'User Joined',
                    'user': UserSerializer(self.scope['user']).data,
                    'message': f"{self.scope['user']} has joined {self.room_name}"
                }
            }
        )
        
        #Join room group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        #Joining personal group.
        await self.channel_layer.group_add(
            self.personal_group,
            self.channel_name
        )
        
        await self.channel_layer.group_send(
            self.personal_group ,
            {
                'type': 'start_game',
            }
        )
        
    async def disconnect(self, code):
        """
        Runs when connection is closed.
        """
        all_members = getattr(self.channel_layer, self.room_group_name, [])
        all_members.remove(self.scope['user'])
        setattr(self.channel_layer, self.room_group_name, all_members)
        
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
                'data': {
                    'context': 'User Left',
                    'user': UserSerializer(self.scope['user']).data,
                    'message': f"{self.scope['user']} has left the session."
                }
            }
        )
    
    async def broadcast(self, event):
        """
        Runs to send the message to all the user.
        """
        data = event['data']
        await self.send(text_data=json.dumps(data))
    
    async def start_game(self, event):
        """
        Starts the game and get all the user in the session.
        """
        all_members = getattr(self.channel_layer, self.room_group_name,[])
        serializer = UserSerializer(all_members, many=True)
        # Send message to personal group
        await self.channel_layer.group_send(
            self.personal_group,
            {
                'type': 'broadcast',
                'data': {
                    'context': 'Game Info',
                    'users': serializer.data,
                    'startTime': json.dumps((str(self.session[0].time_started_at)))
                }
            }
        )   
        
    async def skip_ticket(self, event):
        """
        Skip the current ticket to last.
        """
        pokerboard = self.session[0].pokerboard
        ticket_id = event['message']['ticket']
        if self.scope['user'] == pokerboard.manager and Ticket.objects.get(id=ticket_id).status==Ticket.NOTESTIMATED:
            move_ticket_to_last(pokerboard.id, ticket_id)
    
    async def receive(self, text_data=None, bytes_data=None):
        """
        Runs when receive response from the server.
        """
        try:
            data_json = json.loads(text_data)
            serializer = MethodSerializer(data=data_json)
            serializer.is_valid(raise_exception=True)
            method_name = serializer.validated_data['method_name']
            method_value = serializer.validated_data['method_value']
            fn_name = getattr(self, method_name)
            await fn_name({
                'type':method_name,
                'message':method_value
            })
        except serializers.ValidationError as e:
            await self.send(text_data=json.dumps({'error':'Something went wrong.'}))
        except json.decoder.JSONDecodeError as e:
            await self.send(text_data=json.dumps({'error':'invalid json input'}))
        
    async def final_estimate(self,event):
        """
        Final estimate of ticket set by manager.
        """
        session = Session.objects.get(id=self.scope['url_route']['kwargs']['session_id'])
        deck_type = session.pokerboard.estimation_type
        ticket_key = event['message']['ticket_key']
        estimate = event['message']['estimate']
        if not checkEstimateValue(deck_type, estimate):
            raise ValidationError('Invalid estimate value')
        if self.scope['user'] == self.pokerboard_manager:
            jira = settings.JIRA
            set_estimate = {'customfield_10016':estimate}
            jira.update_issue_field(ticket_key, set_estimate)     
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast',
                    'data': f'Final estimate of {ticket_key} is {estimate}'
                }
            )
            set_user_estimates(self.estimates, ticket_key)
            self.timer = datetime.now()
        else:
            await self.send(text_data=json.dumps({'error':'You do not have permission for this.'}))

    async def estimate(self, event):
        """
        Estimates tickets by user and manager and also update in jira.
        """
        session = Session.objects.get(id=self.scope['url_route']['kwargs']['session_id'])
        deck_type = session.pokerboard.estimation_type
        try:
            ticket_key = event['message']['ticket_key']
            estimate = event['message']['estimate']
            if not checkEstimateValue(deck_type, estimate):
                raise ValidationError('Invalid estimate value')
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast',
                    'data': f"{self.scope['user'].email} has estimated {ticket_key}"
                }
            )

            manager_room_name = 'user_%s' % self.pokerboard_manager.id
            await self.channel_layer.group_send(
                manager_room_name,
                {
                    'type': 'message.manager',
                    'username': self.scope['user'].email,
                    'ticket_key': ticket_key,
                    'estimate': estimate
                }
            )
        except ValidationError as e:
            await self.send(text_data=json.dumps({'error':f'{e}'}))
        except KeyError as e:
            await self.send(text_data=json.dumps({'error':f'{e}'}))
        except requests.exceptions.HTTPError as e:
            await self.send(text_data=json.dumps({'error':f'{e}'}))        

    async def message_manager(self, event):
        """
        Send user estimate to manager
        """
        await self.send(
            text_data=json.dumps
            ({
                'username': event['username'],
                'ticket': event['ticket_key'],
                'estimate': event['estimate'],
            }),
        )
        self.estimates[event['username']] = [event['estimate'], self.timer - datetime.now()]
        
    async def start_timer(self,event):
        self.estimates = {}
        self.timer = datetime.now()
        if self.scope['user'] == self.pokerboard_manager and self.session[0].status == Session.ONGOING:
            self.session.first().time_started_at = timezone.now()
            self.session.first().save()
            # Send message to personal group
            await self.channel_layer.group_send(
                self.room_group_name ,
                {
                    'type': 'broadcast',
                    'data': {
                        'context': 'Timer Started',
                        'startTime': json.dumps(self.session[0].time_started_at.strftime('%H:%M:%S'))
                    }
                }
            )
        else:
            await self.send(text_data=json.dumps({'error':'Cant start time.'}))
