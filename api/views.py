from django.core.cache import cache
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from . import serializers
from . import permissions
from . import models
from utils import email_utils
from services.bot_connector import IntentManipulation


# Create your views here.

page_query = openapi.Parameter('page', openapi.IN_QUERY, description='Página', type=openapi.TYPE_INTEGER)

class CustomUserListCreate(generics.ListAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
 
    @swagger_auto_schema(operation_summary='Retorna todos os usuários')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomUserCurrentRetrieve(generics.RetrieveAPIView):
    serializer_class = serializers.CustomUserRetrieveSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(operation_summary='Retona o usuário atual autorizado')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        cache_key = f'CustomUserCurrentRetrieve_uuid_{self.request.user.uuid}'
        user_cached = cache.get(cache_key)

        if user_cached:
            return user_cached
        else:
            cache.set(cache_key, self.request.user, timeout=60 ** 2 ) # timeout=1 hora

        return self.request.user


class CustomUserByRoleAlunoAPIView(generics.ListAPIView):
    serializer_class = serializers.CustomUserSerializer
    queryset = models.CustomUser.objects.filter(role=2)
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    @swagger_auto_schema(operation_summary='Retona todos os usuários com a role [Aluno]')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomUserChangePasswordAPIView(generics.UpdateAPIView):
    serializer_class = serializers.CustomUserChangePasswordSerializer
    queryset = models.CustomUser.objects.filter(role=2)
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    lookup_field = 'uuid'

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(
        operation_summary='Atualiza a senha de um usuário do tipo [Aluno]',
        operation_description='''
        O Endpoint atualiza a senha de um aluno passando apenas a senha como requisição.
        Temos algumas condições para este endpoint:

        1. Se o usuário que fez a requisição for do tipo **admin**:
            
            * A senha será atualizada.
            * Um email com <u>uma senha provisória será enviado para o aluno</u>.

        2. Se o usuário que fez a requisição for do tipo **aluno**:
            
            * A senha será atualizada normalmente, sem envio de email.
        '''  
    )

    def patch(self, request, *args, **kwargs):
        def update_from_admin(self, request):
            if self.object.is_active:
                return Response({
                    'message': 'Usuário tipo [aluno] já ativo!'
                }, status=status.HTTP_412_PRECONDITION_FAILED)
            
            password = self.request.data.get('password')
            self.object.set_password(password)
            self.object.is_active = True
            self.object.save()
            cache.delete(f'CustomUserCurrentRetrieve_uuid_{self.object.uuid}')

            email_utils.send_email(
                'I.V.O Chat - Nova Senha',
                self.object.email,
                f'''
                Seja bem vindo ao I.V.O Chat! <br>
                Segue sua senha provisória: <br> <br>

                    {password}<br><br>
                
               <strong>OBS:</strong> Terá que trocar a senha após o primeiro login.<br>
                ''',
            )

            return Response({
                'message': 'Senha atualizada com sucesso!',
            }, status=status.HTTP_200_OK)
        
        def update_from_aluno(self, request):
            password = self.request.data.get('password')
            confirm_password = self.request.data.get('confirm_password')
            if confirm_password != password:
                return Response({
                    'message': 'Senhas não coincidem.'
                }, status=status.HTTP_412_PRECONDITION_FAILED)

            self.object.set_password(password)
            self.object.is_password_changed = True
            self.object.save()
            cache.delete(f'CustomUserCurrentRetrieve_uuid_{self.object.uuid}')

            return Response({
                'message': 'Senha atualizada com sucesso!'
            },status=status.HTTP_200_OK)

        self.object = self.get_object()
        response = Response(status=status.HTTP_400_BAD_REQUEST)

        match self.request.user.role:
            case 1:
                response = update_from_admin(self, request) 
            case 2:
                response = update_from_aluno(self, request)
            case _:
                response = Response({
                    'message': 'Tipo de usuário não permitido'
                }, status=status.HTTP_412_PRECONDITION_FAILED)

        return response

class IntentListCreate(views.APIView):
    pauthentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    @swagger_auto_schema(operation_summary='Retorna todas as perguntas', manual_parameters=(page_query,))
    def get(self, request):
        page = int(request.GET.get('page'))

        if not page:
            page = 1

        intent_manipulation = IntentManipulation()
        intents = intent_manipulation.get_all_intents(page)
        intent_serializer = serializers.NLUSerializer(data=intents['data'])

        if intent_serializer.is_valid():
            serialized = intent_serializer.data

            return Response(serialized, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_summary='Cria uma intent', request_body=serializers.IntentSerializer)
    def post(self, request):
        intent_manipulation = IntentManipulation()

        intent_serializer = serializers.IntentSerializer(data=request.data)

        if intent_serializer.is_valid():
            serialized = intent_serializer.data

            res = intent_manipulation.create_intent(serialized)

            if res.status_code == 201:
                return Response(serialized, status=status.HTTP_201_CREATED)

        return Response({}, status=status.HTTP_400_BAD_REQUEST)


class IntentListBy(views.APIView):
    def get(self, request, intent):
        intent_manipulation = IntentManipulation()
        intent = intent_manipulation.get_intent_by_name(intent)

        if not intent:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        intent_serializer = serializers.IntentSerializer(data=intent)

        if intent_serializer.is_valid():
            serialized = intent_serializer.data

            return Response(serialized, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_400_BAD_REQUEST)

class IntentUpdateExamples(views.APIView):

    @swagger_auto_schema(request_body=serializers.IntentExamplesSerializer)
    def patch(self, request, intent):
        intent_manipulation = IntentManipulation()
        print(request.data)
        res = intent_manipulation.edit_intent_examples(intent, request.data)

        if res.status_code != 200:
            return Response({}, status=res.status_code)

        return Response({}, status=200)
