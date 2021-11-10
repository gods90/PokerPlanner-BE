import re

from django.contrib.auth.password_validation import validate_password
from django.conf import settings

from rest_framework import serializers

from group.models import Group
from group.serializer.serializers2 import GetGroupSerializer

from pokerboard.models import PokerboardUserGroup

from user.models import User

from invite.models import Invite

from pokerboard import constants

import jwt


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    invite_id = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'password', 'first_name', 'last_name', 'groups', 'invite_id']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_invite_id(self, attrs):
        try:
            payload = jwt.decode(attrs, settings.SECRET_KEY,
                                 settings.JWT_HASHING_ALGORITHM)
        except Exception as e:
            raise serializers.ValidationError(
                'Token either invalid or expired. Please try with valid token'
            )

        invite_id = payload['invite_id']
        invite = Invite.objects.filter(id=invite_id)
        if not invite.exists():
            raise serializers.ValidationError(
                'Token either invalid or expired. Please try with valid token'
            )
        if invite[0].status is constants.ACCEPTED:
            raise serializers.ValidationError('Invitation already accepted.')
        return invite_id

    def get_groups(self, user):
        res = Group.objects.filter(users__in=[user])
        serializer = GetGroupSerializer(res, many=True)
        return serializer.data

    def create(self, validated_data):
        """
        Overriding create method to hash password and then save.
        """
        invite_id = None
        if 'invite_id' in validated_data.keys():
            invite_id = validated_data['invite_id']
            invite = Invite.objects.get(id=invite_id)
            if invite.email != validated_data['email']:
                raise serializers.ValidationError(
                    'This token was not intended for you.')
            del validated_data['invite_id']
        password = validated_data['password']
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if invite_id is not None:
            invite = Invite.objects.get(id=invite_id)
            invite.status = constants.ACCEPTED
            pokerboarduser_data = {
                'pokerboard_id': invite.pokerboard_id,
                'user': user,
                'role': invite.user_role,
            }
            PokerboardUserGroup.objects.create(**pokerboarduser_data)
            invite.save()
        return user

    def validate_password(self, password):
        """
        To check if password is of atleast length 8,
        has special character,
        has number
        and alphabets.
        """
        reg = "^(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$"

        # compiling regex
        pat = re.compile(reg)

        # searching regex
        mat = re.search(pat, password)
        if not mat:
            raise serializers.ValidationError("Password should be atleast of length 8,"
                                              "one number "
                                              "must contain one uppercase, one lowercase "
                                              "one special character!")
        return super().validate(password)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password')

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance
