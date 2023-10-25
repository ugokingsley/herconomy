from rest_framework import serializers, validators
from django.contrib.auth.hashers import make_password
from . models import *
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from django.http import HttpRequest


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        label=_("Username"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=HttpRequest(),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)

            #if not user:
            #    msg = _('Unable to log in with provided credentials.')
            #    raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('user', 'transaction_type', 'transaction_ref', 'amount', 'narration', )

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

        extra_kwargs = {
            "password": {"write_only": True},
            "email": {
                "required": True,
                "allow_blank": False,
                "validators":[
                    validators.UniqueValidator(
                        User.objects.all(), "A user with this email exists"
                    )
                ]
            }
        }
        