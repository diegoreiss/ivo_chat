from rest_framework import serializers
from drf_yasg import openapi

from . import models


class TurmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Turma
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['uuid', 'pk', 'first_name', 'last_name', 'username', 'email', 'role', 'cpf', 'data_nascimento', 'is_active', 'is_password_changed']


class CustomUserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['uuid', 'pk', 'first_name', 'last_name']


class CustomUserTurmaSerializer(serializers.ModelSerializer):
    turma = TurmaSerializer()

    class Meta:
        model = models.CustomUser
        fields = ['turma']


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


class PendenciasSerializer(serializers.ModelSerializer):
    custom_user = serializers.UUIDField(source='custom_user.uuid', read_only=False)
    custom_user_first_name = serializers.CharField(source='custom_user.first_name', read_only=True)
    custom_user_last_name = serializers.CharField(source='custom_user.last_name', read_only=True)
    custom_user_turma_uuid = serializers.CharField(source='custom_user.turma.uuid', read_only=True)
    custom_user_turma_nome = serializers.CharField(source='custom_user.turma.nome', read_only=True)

    class Meta:
        model = models.Pendencia
        fields = ('uuid', 'descricao', 'status', 
                  'criado_em', 'atualizado_em', 'custom_user', 
                  'custom_user_first_name', 'custom_user_last_name','custom_user_turma_nome',
                  'custom_user_turma_uuid')
        read_only_fields = ('status', 'custom_user', 'custom_user_first_name', 
                            'custom_user_last_name', 'custom_user_turma_nome', 'custom_user_turma_uuid')


class PendenciasCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pendencia
        fields = ('descricao', 'custom_user')


class PendenciaUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pendencia
        fields = ('status', )


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


class ResponseNamesSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.CharField())


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


class StoriesSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {
            'type': openapi.TYPE_OBJECT,
            'title': 'All Stories',
            'properties': {
                'data': openapi.Schema(
                    title='Content of stories',
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        title='Story',
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'story': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='Story name'
                            ),
                            'steps': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                description='Steps of story',
                                items=openapi.Schema(
                                    title='Step',
                                    type=openapi.TYPE_OBJECT,
                                    oneOf=[
                                        openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'intent': openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    description='A intent of step'
                                                ),                                               
                                            }
                                        ),
                                        openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'action': openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    description='A intent of step'
                                                ),                                               
                                            }
                                        ),
                                    ]
                                )
                            )
                        }
                    )
                )
            }
        }


class StoryStepsSerializer(serializers.Serializer):
    steps = serializers.ListField()

    class Meta:
        swagger_schema_fields = {
            'type': openapi.TYPE_OBJECT,
            'title': 'Steps',
            'properties': {
                'steps': openapi.Schema(
                    title='Story Steps',
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        title='Steps',
                        type=openapi.TYPE_OBJECT,
                        oneOf=[
                            openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'intent': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='A intent of step'
                                    )
                                }
                            ),
                            openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'action': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='A action of step'
                                    )
                                }
                            )
                        ]
                    )
                )
            }
        }


class StoryCreateSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {
            'type': openapi.TYPE_OBJECT,
            'title': 'Story',
            'properties': {
                'data': openapi.Schema(
                    title='Story content',
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'story': openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                        'steps': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                oneOf=[
                                    openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'intent': openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description='A intent of step'
                                            )
                                        }
                                    ),
                                    openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'action': openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description='A action of step'
                                            )
                                        }
                                    )
                                ]
                            )
                        )
                    }
                )
            }
        }


class RestInputSendMessageSerializer(serializers.Serializer):
    sender = serializers.CharField()
    message = serializers.CharField()


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
