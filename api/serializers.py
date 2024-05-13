from rest_framework import serializers

from . import models


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['uuid', 'pk', 'first_name', 'last_name', 'username', 'email', 'role', 'cpf', 'data_nascimento', 'is_active', 'is_password_changed']


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['password']


class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['uuid', 'pk', 'first_name', 'last_name', 'username', 'role', 'is_password_changed']


class CustomUserChangePasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField()

    class Meta:
        model = models.CustomUser
        fields = ['password', 'confirm_password']

class IntentSerializer(serializers.Serializer):
    intent = serializers.CharField(default="")
    examples = serializers.CharField(allow_blank=True, required=False, default="")

class IntentExamplesSerializer(serializers.Serializer):
    examples = serializers.CharField()

class NLUSerializer(serializers.Serializer):
    total_pages = serializers.IntegerField()
    nlu = serializers.DictField(child=serializers.ListField(child=IntentSerializer()))
