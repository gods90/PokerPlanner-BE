from rest_framework import serializers

from invite.models import Invite
from invite.tasks import send_invite_email_task
from pokerboard import constants
from pokerboard.models import Pokerboard

from group.models import Group

from user.models import User

class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = '__all__'
        extra_kwargs = {
            'pokerboard': {'read_only': True},
            'user': {'read_only': True},
            'group': {'read_only': True},
        }

    def to_representation(self, instance):
        rep = super(InviteSerializer, self).to_representation(instance)
        rep['user_role'] = constants.ROLE_CHOICES[rep['user_role']][1]
        rep['status'] = constants.INVITE_STATUS[rep['status']][1]
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
    pokerboard = serializers.PrimaryKeyRelatedField(
        queryset=Pokerboard.objects.all())
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False)
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False)
    
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
                pokerboard_manager_email = pokerboard.manager.email
                send_invite_email_task.delay(pokerboard_manager_email, attrs['email'])
                raise serializers.ValidationError("Email to signup in pokerplanner has been sent.Please check your email.")
        else:
            raise serializers.ValidationError('Provide group_id/email!')

        for user in users:
            invite = Invite.objects.filter(
                user=user.id, pokerboard=pokerboard.id)
            if pokerboard.manager == user:
                raise serializers.ValidationError(
                    'Manager cannot be invited!')
            if invite.exists():
                if invite[0].status == constants.ACCEPTED:
                    raise serializers.ValidationError(
                        'Already part of pokerboard')
                elif invite[0].status == constants.PENDING:
                    raise serializers.ValidationError(
                        'Invite already sent!')

        for user in users:
            # invite = Invite.objects.update_or_create( pokerboard_id = pokerboard.id, user_id = user.id, defaults={'status' : constants.PENDING,'user_role' : role})
            try:
                invite = Invite.objects.get(pokerboard_id = pokerboard.id, user_id = user.id)
                invite.status = constants.PENDING
                if 'user_role' in attrs.keys():
                    invite.user_role = attrs['user_role']
                invite.save()
            except Invite.DoesNotExist:
                new_data = {
                    'pokerboard_id' : pokerboard.id,
                    'user_id' : user.id
                }
                if 'user_role' in attrs.keys():
                    new_data['user_role'] = attrs['user_role']
                invite = Invite.objects.create(**new_data)
        return invite

        




    
    
