from rest_framework import serializers

from group.models import Group
from user.models import User
from user.serializer.serializers2 import GetUserSerializer


class GroupSerializer(serializers.ModelSerializer):
    users = GetUserSerializer(many=True,required=False)
    name = serializers.JSONField()
    
    class Meta:
        model = Group
        fields = ['id', 'created_by', 'name','users']
        
    def create(self, validated_data):
        """
        Creates group object with default user as admin
        """
        name = validated_data["name"]
        user = validated_data["created_by"]
        if isinstance(name,list):
            name = name[0]
        group = Group.objects.create(name=name,created_by=user)
        group.users.add(user)
        return group
        
    def validate_name(self,attrs):
        if isinstance(attrs,list) and (not attrs[0] or not(attrs[0].strip())):
                raise serializers.ValidationError("This field cannot be blank.")
        elif isinstance(attrs,list):
            return attrs[0].strip()
        if not attrs or not(attrs.strip()): 
                raise serializers.ValidationError("This field cannot be blank.")
        else:
            return attrs.strip()
        

class GroupUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    
    class Meta:
        model = Group
        fields = ['id', 'created_by', 'name', 'email']

    def validate_email(self, attrs):
        user = User.objects.filter(email=attrs)
        if not user.exists():
            raise serializers.ValidationError('Invalid user!')
        if self.instance.users.filter(email=attrs).exists():
            raise serializers.ValidationError('Already a member!')
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if 'email' not in validated_data:
            raise serializers.ValidationError("This field is required.")
        user = User.objects.get(email=validated_data['email'])
        instance.users.add(user)
        return super().update(instance, validated_data)

