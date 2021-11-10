from django.db.models.query_utils import Q
from rest_framework import serializers

from group.models import Group

from invite.email_send import send_mail
from invite.models import Invite
from invite.tasks import send_invite_email_task

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
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False
    )
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False
    )

    def validate(self, attrs):
        pokerboard_id = self.context['view'].kwargs['pokerboard_id']
        pokerboard = Pokerboard.objects.select_related('manager').get(id=pokerboard_id)
        self.context['view'].kwargs['pokerboard'] = pokerboard
        users = []
        if 'group' in attrs.keys():
            group = attrs['group']
            users = group.users.all()

        elif 'email' in attrs.keys():
            try:
                user = User.objects.get(email=attrs['email'])
                users.append(user)
            except User.DoesNotExist as e:
                pokerboard_manager_email = pokerboard.manager.email
                send_invite_email_task.delay(pokerboard_manager_email, attrs['email'])
                raise serializers.ValidationError("Email to signup in pokerplanner has been sent.Please check your email.")
        else:
            raise serializers.ValidationError('Provide group_id/email!')

        accepted_invites = Invite.objects.filter(
            pokerboard=pokerboard.id, status=constants.ACCEPTED, user__in=[user.id for user in users]
        )
        if accepted_invites.exists():
            raise serializers.ValidationError('Already part of pokerboard')
        
        pending_invites = Invite.objects.filter(
            pokerboard=pokerboard.id, status=constants.PENDING, user__in=[user.id for user in users]
        )
        if pending_invites.exists():
            raise serializers.ValidationError('Invite already sent!')

        if pokerboard.manager in users:
            raise serializers.ValidationError('Manager cannot be invited!')
                    
        return attrs
    
    def create(self, attrs):
        pokerboard = self.context['view'].kwargs['pokerboard']
        users = []
        if 'group' in attrs.keys():
            group = attrs['group']
            users = group.users.all()

        elif 'email' in attrs.keys():
            users = User.objects.filter(email=attrs['email'])
                    
        group = attrs.get('group', None)
        user_role = attrs.get('user_role', constants.PLAYER)
        users_invited = []
        softdeleted_invites = Invite.objects.select_related('user').filter(
            pokerboard_id=pokerboard.id, user__in=users
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
