from rest_framework import serializers

from accounts.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['pk', 'username', 'password', 'email', 'role', 'cpf', 'data_nascimento']


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password', 'email']
