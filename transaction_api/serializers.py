from rest_framework import serializers, validators
from django.contrib.auth.hashers import make_password
from . models import *


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
        