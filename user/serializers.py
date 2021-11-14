import jwt
import re 

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.db.models.query_utils import Q

from django.contrib.auth.password_validation import validate_password
from django.conf import settings

from group.models import Group

from pokerboard import constants
from pokerboard.models import PokerboardUserGroup, Pokerboard, Ticket

from invite.models import Invite
from pokerplanner.settings import JIRA
from session.models import UserEstimate

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user
    """
    invite_id = serializers.CharField(required=False, write_only=True)
    groups = serializers.SerializerMethodField()
    pokerboards = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'password', 'first_name', 'last_name', 'groups', 'invite_id', 'token', 'pokerboards']
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
        invite = invite.first()
        if invite.status is constants.ACCEPTED:
            raise serializers.ValidationError('Invitation already accepted.')
        self.context['invite'] = invite
        return invite_id

    def get_groups(self, user):
        from group.serializers import GetGroupSerializer
        res = Group.objects.filter(users__in=[user])
        serializer = GetGroupSerializer(res, many=True)
        return serializer.data
    
    def get_token(self, user):
        token, _ = Token.objects.get_or_create(user_id=user.id)
        return token.key

    def get_pokerboards(self, user):
        from pokerboard.serializers import PokerboardUserProfileSerializer
        res = Pokerboard.objects.filter(
                Q(manager=user)| Q(invite__email=user.email,invite__status=constants.ACCEPTED
            )).distinct()
        serializer = PokerboardUserProfileSerializer(res, many=True)
        return serializer.data
        
    def create(self, validated_data):
        """
        Overriding create method to check jwt.
        """
        invite_id = None
        if 'invite_id' in validated_data.keys():
            invite = self.context['invite']
            if invite.email != validated_data['email']:
                raise serializers.ValidationError('This token was not intended for you.')
            del validated_data['invite_id']
        user = User(**validated_data)
        user.save()
        if invite_id is not None:
            invite = self.context['invite']
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


class GetUserSerializer(serializers.ModelSerializer):
    """
    Serializer to get user details.
    """
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'id']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password')

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class EstimateSerializer(serializers.ModelSerializer):
    """
    Serializer to get estimate
    """
    actual_estimate = serializers.SerializerMethodField()
    ticket = serializers.CharField(source='ticket.jira_id')
    class Meta:
        model = UserEstimate
        fields = ['id', 'actual_estimate', 'estimation_duration', 'estimate', 'ticket']
    
    def get_actual_estimate(self, instance):
        ticket_jira_id = Ticket.objects.get(id=instance.ticket_id).ticket_id
        try:
            jira_response = JIRA.issue(key=ticket_jira_id)['fields']
            return jira_response['customfield_10016']
        except Exception as e:
            raise serializers.ValidationError(e)
