import re

from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

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


