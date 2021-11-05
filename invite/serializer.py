from rest_framework import serializers

from group.models import Group

from invite.email_send import send_mail
from invite.models import Invite

from pokerboard import constants
from pokerboard.models import Pokerboard

from user.models import User


class InviteSerializer(serializers.ModelSerializer):
    """
    Serializer for update, soft-delete of invites
    """
    user_role = serializers.CharField(source='get_user_role_display')
    status = serializers.CharField(source='get_status_display')
    pokerboard_title = serializers.CharField(source='pokerboard')

    class Meta:
        model = Invite
        fields = ['id', 'status', 'pokerboard', 'user', 'group', 'user_role', 'pokerboard_title']
        extra_kwargs = {
            'pokerboard': {'read_only': True},
            'user': {'read_only': True},
            'group': {'read_only': True},
        }
    
    def validate(self, attrs):
        invite = attrs['invite_id']
        if invite.status == constants.DECLINED:
            raise serializers.ValidationError('Invite doesnt exist!')
        if invite.status == constants.ACCEPTED:
            raise serializers.ValidationError('Invite already accepted!')
        return super().validate(attrs)
    
    
class InviteCreateSerializer(serializers.Serializer):
    """
    Serializer to create new invite to pokerboard
    """
    pokerboard = serializers.PrimaryKeyRelatedField(
        queryset=Pokerboard.objects.all()
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False
    )
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False
    )
    
    def create(self, attrs):
        pokerboard = attrs['pokerboard']
        users = []
        if 'group' in attrs.keys():
            group = attrs['group']
            users = group.users.all()

        elif 'email' in attrs.keys():
            users = User.objects.filter(email=attrs['email'])
            if not users.exists():
                send_mail(to_emails=[attrs['email']])
                raise serializers.ValidationError(
                    "Invitation to pokerboard will be sent."
                )
        else:
            raise serializers.ValidationError('Provide group_id/email!')

        for user in users:
            invite = Invite.objects.filter(
                user=user.id, pokerboard=pokerboard.id
            )
            if pokerboard.manager == user:
                raise serializers.ValidationError(
                    'Manager cannot be invited!'
                )
            if invite.exists():
                if invite[0].status == constants.ACCEPTED:
                    raise serializers.ValidationError(
                        'Already part of pokerboard'
                    )
                elif invite[0].status == constants.PENDING:
                    raise serializers.ValidationError(
                        'Invite already sent!'
                    )
                    
        group = attrs.get('group', None)
        user_role = attrs.get('user_role', constants.PLAYER)
        users_invited = []
        softdeleted_invites = (
                        Invite.objects.select_related('user').
                            filter(pokerboard_id=pokerboard.id, user__in=users)
        )
        
        for softdeleted_invite in softdeleted_invites:
            softdeleted_invite.group = group
            softdeleted_invite.user_role = user_role
            softdeleted_invite.status = constants.PENDING
            users_invited.append(softdeleted_invite.user.id)
            
        remaining_users = users.exclude(id__in=users_invited)
        Invite.objects.bulk_create(
            [
                Invite(
                    pokerboard_id=pokerboard.id, user=user,
                    group=group, user_role=user_role
                ) for user in remaining_users
            ]
        )
        Invite.objects.bulk_update(
            softdeleted_invites, ['group', 'user_role', 'status']
        )
        return attrs
