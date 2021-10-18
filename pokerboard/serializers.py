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
                user_id=user[0].id, pokerboard_id=pokerboard_id)
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


class PokerBoardSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    ticket = TicketSerializer(source='ticket_set', many=True)

    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'configuration', 'status', 'ticket']


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())

    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'configuration']


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
        method = self.context['method']
        users = []

        if method in ['DELETE', 'POST']:
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
                raise serializers.ValidationError('Provide group_id/email!')

            pokerboard = Pokerboard.objects.get(id=pokerboard_id)
            for user in users:

                if pokerboard.manager == user:
                    raise serializers.ValidationError(
                        'Manager cannot be invited!')

                invite = Invite.objects.filter(
                    user=user.id, pokerboard=pokerboard_id)

                if method == 'POST' and invite.exists():
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
            if not invite.exists():
                raise serializers.ValidationError('Invite doesnt exists')
            if invite.exists() and invite[0].is_accepted:
                raise serializers.ValidationError('Invite already accepted!')

        return super().validate(attrs)
