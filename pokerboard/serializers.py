from rest_framework import serializers

from group.models import Group
from pokerboard import constants
from pokerboard.models import Invite, Pokerboard, PokerboardUserGroup, Ticket
from pokerboard.email_send import send_mail
from user.models import User

from pokerplanner import settings


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['pokerboard', 'ticket_id',
                  'order', 'estimation_date', 'status']


class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class PokerboardUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokerboardUserGroup
        fields = ['id', 'user', 'group', 'role', 'pokerboard']


class PokerboardMembersSerializer(serializers.Serializer):
    pokerboard_id = serializers.PrimaryKeyRelatedField(
        queryset=Pokerboard.objects.all())
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False)
    email = serializers.EmailField(required=False)
    role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False)

    def validate(self, attrs):
        pokerboard_id = attrs['pokerboard_id']
        method = self.context['method']

        if 'email' in attrs.keys():
            user = User.objects.filter(email=attrs['email'])
            if not user.exists():
                raise serializers.ValidationError('Invalid email!')

            pokerboard_user = PokerboardUserGroup.objects.filter(
                user_id=user[0].id, pokerboard_id=pokerboard_id.id)
            if not pokerboard_user.exists():
                raise serializers.ValidationError(
                    'User not member of pokerboard!')

        if method == 'DELETE':
            if 'group_id' in attrs.keys():
                group = attrs['group_id']

                pokerboard_members = PokerboardUserGroup.objects.filter(
                    pokerboard_id=pokerboard_id, group_id=group.id)
                if not pokerboard_members.exists():
                    raise serializers.ValidationError('No members found!')

            elif 'email' not in attrs.keys():
                raise serializers.ValidationError('Provide group_id/email!')

        elif method == 'PATCH':
            if 'role' not in attrs.keys():
                raise serializers.ValidationError('Role not provided!')
            if pokerboard_user[0].role == attrs['role']:
                raise serializers.ValidationError('User already in same role.')
        return attrs


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())

    # manager_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # sprint_id = serializers.CharField(required=False,write_only=True)
    # tickets = TicketsSerializer(required=False,write_only=True)
    # jql = serializers.CharField(required=False,write_only=True)
    # ticket_responses = serializers.SerializerMethodField()

    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'configuration']

    # class Meta:
    #     model = Pokerboard
    #     fields = ['manager_id', 'title', 'description','configuration', 'tickets', 'sprint_id', 'ticket_responses', 'jql']

    # def get_ticket_responses(self, instance):
    #     jira = settings.JIRA
    #     data = dict(instance)
    #     ticket_responses = []

    #     myJql=""
    #     # If sprint, then fetch all tickets in sprint and add
    #     if 'sprint_id' in data.keys():
    #         myJql = "Sprint = "+ data['sprint_id']

    #     # Adding tickets
    #     if 'tickets' in data.keys():
    #         tickets = data['tickets']
    #         serializer = TicketsSerializer(data=tickets)
    #         serializer.is_valid(raise_exception=True)

    #         if(len(myJql) != 0):
    #             myJql+=" OR "
    #         myJql += "issueKey in ("
    #         for ticket in tickets:
    #             myJql = myJql + ticket + ','
    #         myJql = myJql[:-1] +')'

    #     # Adding jql
    #     if 'jql' in data.keys():
    #         if(len(myJql) != 0):
    #             myJql+=" OR "
    #         myJql += data['jql']

    #     jql=myJql
    #     try:
    #         issues = jira.jql(jql)['issues']
    #         for issue in issues:
    #             ticket_response = {}
    #             key = issue['key']
    #             obj = Ticket.objects.filter(ticket_id=key)
    #             if obj.exists():
    #                 ticket_response['message'] = 'Ticket part of another pokerboard.'
    #                 ticket_response['status_code'] = status.HTTP_400_BAD_REQUEST
    #             else:
    #                 ticket_response['estimate'] = issue['fields']['customfield_10016']
    #                 ticket_response['status_code'] = status.HTTP_200_OK
    #             ticket_response['key'] = key
    #             ticket_responses.append(ticket_response)
    #     except requests.exceptions.RequestException as e:
    #         raise serializers.ValidationError("Invalid Query")
    #     return ticket_responses

    # def create(self, validated_data):
    #     count = 0
    #     new_pokerboard = {key: val for key, val in self.data.items() if key not in [
    #         'sprint_id', 'tickets', 'jql']}
    #     ticket_responses = new_pokerboard.pop('ticket_responses')

    #     valid_tickets = 0
    #     for ticket_response in ticket_responses:
    #         valid_tickets += ticket_response['status_code'] == 200

    #     if valid_tickets == 0:
    #         raise serializers.ValidationError('Invalid tickets!')

    #     pokerboard = Pokerboard.objects.create(**new_pokerboard)

    #     for ticket_response in ticket_responses:
    #         if ticket_response['status_code'] != 200:
    #             continue
    #         new_ticket_data = {}
    #         new_ticket_data['pokerboard'] = pokerboard
    #         new_ticket_data['ticket_id'] = ticket_response['key']
    #         new_ticket_data['order'] = count
    #         Ticket.objects.create(**new_ticket_data)
    #         count += 1
    #     return pokerboard


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = '__all__'
        extra_kwargs = {
            'is_accepted': {'read_only': True}
        }

    def to_representation(self, instance):
        rep = super(InviteSerializer, self).to_representation(instance)
        rep['user_role'] = constants.ROLE_CHOICES[rep['user_role']][1]
        rep['pokerboard_title'] = instance.pokerboard.title
        return rep


class InviteCreateSerializer(serializers.Serializer):
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False)
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False)

    def validate(self, attrs):
        pokerboard_id = self.context['pokerboard_id']
        method = self.context['method']
        users = []
        pokerboard = Pokerboard.objects.get(id=pokerboard_id)

        if method in ['DELETE', 'POST']:
            if 'group_id' in attrs.keys():
                group = attrs['group_id']
                users = group.users.all()

            elif 'email' in attrs.keys():
                try:
                    user = User.objects.get(email=attrs['email'])
                    users.append(user)
                except User.DoesNotExist as e:
                    send_mail(to_emails=[attrs['email']])
                    raise serializers.ValidationError(
                        "Email to signup in pokerplanner has been sent.Please check your email.")
            else:
                raise serializers.ValidationError('Provide group_id/email!')

            for user in users:
                invite = Invite.objects.filter(
                    user=user.id, pokerboard=pokerboard_id)
                if method == 'POST':
                    if pokerboard.manager == user:
                        raise serializers.ValidationError(
                            'Manager cannot be invited!')
                    if invite.exists():
                        if invite[0].is_accepted:
                            raise serializers.ValidationError(
                                'Already part of pokerboard')
                        else:
                            raise serializers.ValidationError(
                                'Invite already sent!')

                elif method == 'DELETE':
                    if not invite.exists():
                        raise serializers.ValidationError('User not invited!')
                    elif invite.exists() and invite[0].is_accepted:
                        raise serializers.ValidationError(
                            'Accepted invites cannot be revoked.')

        elif method in ['PATCH']:
            user = self.context['user']
            invite = Invite.objects.filter(
                user_id=user.id, pokerboard_id=pokerboard_id)
            pokerboard = Pokerboard.objects.get(id=pokerboard_id)
            if pokerboard.manager == user:
                raise serializers.ValidationError('Already manager!')
            if not invite.exists():
                raise serializers.ValidationError('Invite doesnt exists')
            if invite.exists() and invite[0].is_accepted:
                raise serializers.ValidationError(
                    'Already part of pokerboard.')

        return super().validate(attrs)
