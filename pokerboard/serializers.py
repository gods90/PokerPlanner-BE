from rest_framework import serializers
from pokerboard import constants

from pokerboard.models import Invite, Pokerboard, PokerboardUserGroup, Ticket

from user.models import User
from user.serializers import UserSerializer

from group.models import Group


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


class PokerboardUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False)

    def validate_email(self, attrs):
        pokerboard_id = self.context['pk']
        user = User.objects.filter(email=self.context['email'])

        if not user.exists():
            raise serializers.ValidationError('Invalid user!')
            
        pokerboard_user = PokerboardUserGroup.objects.filter(
            pokerboard_id=pokerboard_id, user_id=user[0].id)
        if not pokerboard_user.exists():
            raise serializers.ValidationError(
                'User not a member of pokerboard!')

        return attrs


class PokerBoardSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    ticket = TicketSerializer(source='ticket_set', many=True)

    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'configuration', 'status', 'ticket']


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    sprint_id = serializers.CharField(required=False)
    tickets = TicketsSerializer(required=False)

    class Meta:
        model = Pokerboard
        fields = ['manager_id', 'title', 'description',
                  'configuration', 'tickets', 'sprint_id']


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = '__all__'
        extra_kwargs = {
            'is_accepted': {'read_only': True}
        }


class InviteCreateSerializer(serializers.Serializer):
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False)
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False)

    def validate(self, attrs):
        pokerboard_id = self.context['pokerboard_id']
        users = []

        if 'group_id' in attrs.keys():
            group = attrs['group_id']
            users = group.users.all()
        elif 'email' in attrs.keys():
            try:
                user = User.objects.get(email=attrs['email'])
                users.append(user)
            except User.DoesNotExist as e:
                # TODO Send mail to user
                raise serializers.ValidationError(e)
        else:
            raise serializers.ValidationError('Invalid group/email!')

        for user in users:
            invite = Invite.objects.filter(
                user=user.id, pokerboard=pokerboard_id)
            if invite.exists():
                if invite[0].is_accepted:
                    raise serializers.ValidationError(
                        'Already part of pokerboard')
                else:
                    raise serializers.ValidationError('Invite already sent!')

        return super().validate(attrs)
