from rest_framework import serializers
from drf_yasg import openapi

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

class IntentNamesSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.CharField())

class NLUSerializer(serializers.Serializer):
    total_pages = serializers.IntegerField()
    nlu = serializers.DictField(child=serializers.ListField(child=IntentSerializer()))

class UtterSerializer(serializers.Serializer):
    total_pages = serializers.IntegerField()
    responses = serializers.JSONField()

class DynamicResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {
            'type': openapi.TYPE_OBJECT,
            'title': 'Response',
            'properties': {
                'utter_<nome_da_intent>': openapi.Schema(
                    title='response name',
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        title='text of response',
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'text': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='text of response'
                            )
                        }
                    )
                ),
            },
            'required': ['utter_<nome_da_intent>']
        }
    def to_representation(self, instance):
        return instance
    
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError('Esperando um dicionário de dados')

        if len(data) != 1:
            raise serializers.ValidationError('Deve haver apenas uma chave no dicionário')
        
        key: str = list(data.keys())[0]

        if not key.startswith('utter_'):
            raise serializers.ValidationError('O valor da key deve começar com "utter_".')

        if not isinstance(data[key], list):
            raise serializers.ValidationError(f'O valor da key "{key}" deve ser uma lista')
        
        if not len(data[key]) or len(data[key]) > 1:
            raise serializers.ValidationError('A chave não pode ter valores vazios e não pode passar de 1 item')
        
        for item in data[key]:
            if not isinstance(item, dict) or 'text' not in item:
                raise serializers.ValidationError(f'Cada item da key "{key}" deve ter um dicionário contendo a chave "text" ')
        
        return data
    
    def validate(self, data):
        return data

class ResponseTextsSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {
            'type': openapi.TYPE_OBJECT,
            'title': 'Response Texts',
            'properties': {
                'texts': openapi.Schema(
                    title='texts of response',
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        title='texts of response',
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'text': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='text of response'
                            )
                        }
                    )
                )
            }
        }

    texts = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    