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
    class Meta:
        model = Invite
        fields = ['id', 'status', 'pokerboard', 'user', 'group', 'user_role']
        extra_kwargs = {
            'pokerboard': {'read_only': True},
            'user': {'read_only': True},
            'group': {'read_only': True},
        }

    def to_representation(self, instance):
        rep = super(InviteSerializer, self).to_representation(instance)
        rep['pokerboard_title'] = instance.pokerboard.title
        return rep
    
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
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False
    )
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False
    )
    
    def create(self, attrs):
        pokerboard = attrs['pokerboard']
        users = []
        if 'group_id' in attrs.keys():
            group = attrs['group_id']
            users = group.users.all()

        elif 'email' in attrs.keys():
            try:
                user = User.objects.get(email=attrs['email'])
                users.append(user)
            except User.DoesNotExist as e:
                send_mail(to_emails=[attrs['email']])
                raise serializers.ValidationError("Email to signup in pokerplanner has been sent.Please check your email.")
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

        for user in users:
            try:
                invite = Invite.objects.get(pokerboard_id = pokerboard.id, user_id = user.id)
                invite.status = constants.PENDING
                if 'user_role' in attrs.keys():
                    invite.user_role = attrs['user_role']
                invite.save()
            except Invite.DoesNotExist:
                new_data = {
                    'pokerboard_id' : pokerboard.id,
                    'user_id' : user.id,
                }
                if 'group_id' in attrs.keys():
                    new_data['group_id'] = attrs['group_id'].id
                if 'user_role' in attrs.keys():
                    new_data['user_role'] = attrs['user_role']
                invite = Invite.objects.create(**new_data)
        return invite

