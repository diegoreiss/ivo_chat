from rest_framework import serializers

from accounts.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['pk', 'first_name', 'last_name', 'username', 'email', 'role', 'cpf', 'data_nascimento', 'is_active', 'is_password_changed']


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password']


class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['pk', 'first_name', 'last_name', 'username', 'role', 'is_password_changed']


class CustomUserChangePasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['password', 'confirm_password']
