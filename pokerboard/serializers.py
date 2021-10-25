from rest_framework import serializers

from group.models import Group
from pokerboard import constants
from pokerboard.models import Pokerboard, PokerboardUserGroup
from user.models import User


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
    
    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'configuration']

           


