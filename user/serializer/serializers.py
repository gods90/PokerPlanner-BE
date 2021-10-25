import re

from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from group.models import Group
from group.serializer.serializers2 import GetGroupSerializer
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'password', 'first_name', 'last_name', 'groups']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_groups(self, user):
        res = Group.objects.filter(users__in=[user])
        serializer = GetGroupSerializer(res, many=True)
        return serializer.data

    def create(self, validated_data):
        """
        Overriding create method to hash password and then save.
        """
        password = validated_data['password']
        user = User(**validated_data)
        user.set_password(password)
        user.save()
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
