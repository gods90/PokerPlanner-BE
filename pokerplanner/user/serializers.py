import re
from rest_framework import serializers
from pokerplanner.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, password):
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$"
      
         # compiling regex
        pat = re.compile(reg)
      
        # searching regex                 
        mat = re.search(pat, password)
        print(mat)
        if not mat:
            raise serializers.ValidationError("Password should be atleast of length 8,"
                                               "one number "
                                               "must contain one uppercase, one lowercase " 
                                               "one special character!")
        return super().validate(password)