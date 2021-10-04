import re
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from pokerplanner.user.models import User


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name','token']
        extra_kwargs = {
            'password': {'write_only': True}
        }

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

    def get_token(self, obj):
        """
        To add token in the response.
        """
        token, _ = Token.objects.get_or_create(user=obj)
        return token.key


class UserSerializerToken(serializers.Serializer):
    """
    Serializer to validate data when user is logging in.
    """
    email = serializers.EmailField()
    password = serializers.CharField()
