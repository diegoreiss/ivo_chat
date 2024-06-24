import os
import uuid
import mimetypes
import statistics
from urllib.parse import urljoin

from django.core.cache import cache, caches
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.db.models import Count, Case, When, BooleanField
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_api_key.permissions import HasAPIKey
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from . import serializers
from . import permissions
from . import models
from utils import email_utils, pdf_utils
from services.bot_connector import (
    IntentManipulation, ResponseManipulation, StoriesManipulation,
    RestInput, BotMetricsInput
)


# Create your views here.

page_query = openapi.Parameter('page', openapi.IN_QUERY, description='Página', type=openapi.TYPE_INTEGER, required=True, default=1)


class Ping(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    @swagger_auto_schema(operation_summary='Health Check')
    def get(self, request):
        return Response({'result': 'pong'}, status=status.HTTP_200_OK)


class CustomUserListCreate(generics.ListAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
 
    @swagger_auto_schema(operation_summary='Retorna todos os usuários')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomUserTurmaRetrieve(generics.RetrieveAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.CustomUserTurmaSerializer
    lookup_field = 'uuid'
    authentication_classes = ()
    permission_classes = (HasAPIKey, )


class CustomUserCurrentRetrieve(generics.RetrieveAPIView):
    serializer_class = serializers.CustomUserRetrieveSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(operation_summary='Retona o usuário atual autorizado')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        cache_key = f'users_data:CustomUserCurrentRetrieve_uuid_{self.request.user.uuid}'
        user_cached = cache.get(cache_key)

        if user_cached:
            return user_cached
        else:
            cache.set(cache_key, self.request.user, timeout=60 ** 2 ) # timeout=1 hora

        return self.request.user


class CustomUserMinimalRetrieve(generics.RetrieveAPIView):
    serializer_class = serializers.CustomUserMinimalSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
            cache.delete(f'users_data:CustomUserCurrentRetrieve_uuid_{self.object.uuid}')

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
            cache.delete(f'users_data:CustomUserCurrentRetrieve_uuid_{self.object.uuid}')

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


class CustomUserRetrieveTurmaCount(views.APIView):
    authentication_classes = ()
    permission_classes = (HasAPIKey,)

    @swagger_auto_schema(operation_summary='1')
    def get(self, request, turma_uuid, *args, **kwargs):
        count = models.CustomUser.objects.filter(turma__uuid=uuid.UUID(turma_uuid)).count()
        return Response({'count': count})


class CustomUserRetrieveAllCount(views.APIView):
    authentication_classes = ()
    permission_classes = ()
    pagination_class = None


    manual_parameters = [
        'all', 'active', 'inactive'
    ]
    @swagger_auto_schema(operation_summary='2', manual_parameters=[
        openapi.Parameter(
            'filter_by',
            openapi.IN_QUERY,
            description='Filter by',
            type=openapi.TYPE_STRING,
            enum=manual_parameters,
            default=manual_parameters[0]
        )
    ])
    def get(self, request, *args, **kwargs):
        filter_by = request.GET.get('filter_by', 'all')

        if filter_by == self.manual_parameters[1]:
            count = models.CustomUser.objects.filter(is_active=True).count()
        elif filter_by == self.manual_parameters[2]:
            count = models.CustomUser.objects.filter(is_active=False).count()
        else:
            count = models.CustomUser.objects.all().count()
        

        return Response({'count': count}, status=status.HTTP_200_OK)


class CustomUserMetrics(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    manual_parameters = [
        'count_is_active_for_each_custom_user', 'total_users'
    ]

    @swagger_auto_schema(operation_summary='Métricas disponíveis para CustomUser', manual_parameters=[
        openapi.Parameter(
            'metrics',
            openapi.IN_QUERY,
            description='Available metrics',
            type=openapi.TYPE_STRING,
            enum=manual_parameters,
            default=manual_parameters[0]
        )
    ])
    def get(self, request, *args, **kwargs):
        metrics = request.GET.get('metrics', self.manual_parameters[0])

        if metrics == self.manual_parameters[0]:
            alunos = models.CustomUser.objects.filter(role=2).aggregate(
                total_alunos=Count('id'),
                com_acesso=Count(Case(When(is_active=True, then=1), output_field=BooleanField())),
                sem_acesso=Count(Case(When(is_active=False, then=1), output_field=BooleanField()))
            )
            return Response(alunos, status=status.HTTP_200_OK)


class PendenciasListCreate(generics.ListCreateAPIView):
    queryset = models.Pendencia.objects.all()
    serializer_class = serializers.PendenciasSerializer
    authentication_classes = ()
    permission_classes = (HasAPIKey,)

    @swagger_auto_schema(operation_summary='Retorna todas as pendências')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_summary='Cria uma pendência')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        custom_user_uuid = request.data['custom_user']
        user = models.CustomUser.objects.get(uuid=custom_user_uuid)
        request_data = request.data.copy()
        request_data['custom_user'] = user.pk
        serializer = serializers.PendenciasCreateSerializer(data=request_data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        return Response(status=status.HTTP_201_CREATED, headers=headers)


class PendenciaMetrics(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    manual_parameters = [
        'count_pendencia_for_each_turma', 'count_pendencia_status'
    ]

    @swagger_auto_schema(operation_summary='Métricas disponíveis', manual_parameters=[
        openapi.Parameter(
            'metrics',
            openapi.IN_QUERY,
            description='Metrics for pendência',
            type=openapi.TYPE_STRING,
            enum=manual_parameters,
            default=manual_parameters[0]
        )
    ])
    def get(self, request, *args, **kwargs):
        metrics = request.GET.get('metrics', self.manual_parameters[0])

        if metrics == self.manual_parameters[0]:
            turmas = models.Turma.objects.annotate(num_pendencias=Count('customuser__pendencia'))

            return Response({'turmas': {f'{turma.nome} - {turma.TURNO_CHOICES[turma.turno - 1][1]}': turma.num_pendencias for turma in turmas}}, status=status.HTTP_200_OK)
        elif metrics == self.manual_parameters[1]:
            pendencias_status = models.Pendencia.objects.aggregate(
                pendencias_aguardando_resposta=Count(Case(When(status=1, then=1), output_field=BooleanField())),
                pendencias_resolvidas=Count(Case(When(status=2, then=1), output_field=BooleanField())),
            )

            return Response(pendencias_status, status=status.HTTP_200_OK)


class PendenciasListByCustomUser(generics.ListAPIView):
    authentication_classes = ()
    permission_classes = (HasAPIKey, )
    serializer_class = serializers.PendenciasSerializer

    def get_queryset(self):
        aluno_uuid = self.kwargs['aluno_uuid']

        return models.Pendencia.objects.filter(custom_user__uuid=aluno_uuid)


class PendenciasUpdateStatus(generics.UpdateAPIView):
    authentication_classes = ()
    permission_classes = (HasAPIKey, )
    serializer_class = serializers.PendenciaUpdateStatusSerializer
    queryset = models.Pendencia.objects.all()
    lookup_field = 'uuid'

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class IntentListCreate(views.APIView):
    authentication_classes = (JWTAuthentication, )
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


class IntentNamesList(views.APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    def get(self, request):
        intent_manipulation = IntentManipulation()
        intents_names = intent_manipulation.get_all_intents_names()
        intents_names_serializer = serializers.IntentNamesSerializer(data=intents_names)

        if intents_names_serializer.is_valid():
            serialized = intents_names_serializer.data

            return Response(serialized, status=status.HTTP_200_OK)

        return Response({}, status=400)
        

class AvailableIntentNamesList(views.APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    def get(self, request):
        intent_manipulation = IntentManipulation()
        available_intents_names = intent_manipulation.get_all_available_intents_names()

        if available_intents_names.status_code == 200:
            intents_names_serializer = serializers.IntentNamesSerializer(data=available_intents_names.json())

            if intents_names_serializer.is_valid():
                serialized = intents_names_serializer.data

                return Response(serialized, status=available_intents_names.status_code)

        return Response({}, status=400)


class IntentListBy(views.APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

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
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    @swagger_auto_schema(request_body=serializers.IntentExamplesSerializer)
    def patch(self, request, intent):
        intent_manipulation = IntentManipulation()
        res = intent_manipulation.edit_intent_examples(intent, request.data)

        if res.status_code != 200:
            return Response({}, status=res.status_code)

        return Response({}, status=200)

class ResponseRetrieveCreate(views.APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    @swagger_auto_schema(manual_parameters=(page_query,))
    def get(self, request):
        page = int(request.GET.get('page'))

        if not page:
            page = 1

        res_manipulation = ResponseManipulation()
        responses = res_manipulation.get_all_responses(page)
        res_json = responses.json()

        response_serializer = serializers.UtterSerializer(data=res_json['data'])

        if response_serializer.is_valid():
            return Response(response_serializer.data, status=200)

        return Response({}, status=200)
    
    @swagger_auto_schema(
        request_body=serializers.DynamicResponseSerializer
    )
    def post(self, request):
        response_serializer = serializers.DynamicResponseSerializer(data=request.data)

        if response_serializer.is_valid():
            serialized = response_serializer.data
            response_manipulation = ResponseManipulation()
            res_json = response_manipulation.create_response(serialized)

            if res_json.status_code == status.HTTP_201_CREATED:
                return Response({}, status=res_json.status_code)

        return Response({}, status=400)


class ResponseNamesRetrieve(views.APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    @swagger_auto_schema(responses={
        status.HTTP_200_OK: openapi.Response(
            description='Success Response',
            schema=serializers.ResponseNamesSerializer
        )
    })
    def get(self, request):
        response_manipulation = ResponseManipulation()
        res = response_manipulation.get_all_responses_names()

        match res.status_code:
            case status.HTTP_400_BAD_REQUEST | \
                status.HTTP_401_UNAUTHORIZED | \
                status.HTTP_403_FORBIDDEN:

                return Response({}, status=res.status_code)
            case status.HTTP_200_OK:
                return Response(res.json(), status=res.status_code)
            case _:
                return Response({}, status=res.status_code)


class ResponsesUpdateTexts(views.APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    @swagger_auto_schema(request_body=serializers.ResponseTextsSerializer)
    def patch(self, request, response_name):
        response_manipulation = ResponseManipulation()
        response_text_serializer = serializers.ResponseTextsSerializer(data=request.data)

        if response_text_serializer.is_valid():
            res = response_manipulation.edit_response_examples(response_name, request.data)

            if res.status_code == status.HTTP_200_OK:
                return Response({}, status=res.status_code)
        
        return Response({}, status=400)


class StoriesListCreate(views.APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    @swagger_auto_schema(responses={
        status.HTTP_200_OK: openapi.Response(
            description='Success Response',
            schema=serializers.StoriesSerializer
        )
    })
    def get(self, request):
        stories_manipulation = StoriesManipulation()
        res = stories_manipulation.get_all_stories()

        match res.status_code:
            case status.HTTP_400_BAD_REQUEST | \
                 status.HTTP_401_UNAUTHORIZED | \
                 status.HTTP_403_FORBIDDEN:
                return Response({}, status=res.status_code)
            case status.HTTP_200_OK:
                return Response(res.json(), status=res.status_code)
            case _:
                return Response({}, status=res.status_code)
    
    @swagger_auto_schema(request_body=serializers.StoryCreateSerializer)
    def post(self, request):
        stories_manipulation = StoriesManipulation()
        result = stories_manipulation.create_story(request.data)

        match result.status_code:
            case status.HTTP_400_BAD_REQUEST | \
                status.HTTP_401_UNAUTHORIZED | \
                status.HTTP_403_FORBIDDEN:
                
                return Response({}, status=result.status_code)
            case status.HTTP_201_CREATED:
                return Response({}, status=result.status_code)

        return Response({}, status=418)


class StoriesStepsUpdate(views.APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IsAdmin)

    @swagger_auto_schema(request_body=serializers.StoryStepsSerializer)
    def patch(self, request, story):
        stories_steps_serializer = serializers.StoryStepsSerializer(data=request.data)

        if not stories_steps_serializer.is_valid():
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        stories_manipulation = StoriesManipulation()
        res = stories_manipulation.change_story_steps(story, stories_steps_serializer.data)

        match res.status_code:
            case status.HTTP_400_BAD_REQUEST | \
                status.HTTP_401_UNAUTHORIZED | \
                status.HTTP_403_FORBIDDEN:

                return Response({}, status=res.status_code)
            case status.HTTP_200_OK:
                return Response({}, status=res.status_code)
            case _:
                return Response({}, status=res.status_code)


class MessageToBotSender(views.APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=serializers.RestInputSendMessageSerializer)
    def post(self, request):
        print(request)

        rest_input_send_message_serializer = serializers.RestInputSendMessageSerializer(data=request.data)

        if not rest_input_send_message_serializer.is_valid():
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        
        rest_input = RestInput()
        res = rest_input.send_message_to_bot(rest_input_send_message_serializer.data)

        match res.status_code:
            case status.HTTP_400_BAD_REQUEST:
                return Response({}, status=res.status_code)
            case status.HTTP_200_OK:
                return Response(res.json(), status=res.status_code)

        return Response({'valid': rest_input_send_message_serializer.is_valid()}, status=418)


class BotMetrics(views.APIView):
    authentication_classes = ()
    permission_classes = (HasAPIKey,)

    @swagger_auto_schema(operation_summary='Retorna as métricas do bot')
    def get(self, request):
        bot_metrics = BotMetricsInput()
        metrics = bot_metrics.get_all_metrics()
        metrics_json = metrics.json()

        return Response(metrics_json, status=200)


class AppMetrics(views.APIView):
    authentication_classes = ()
    permission_classes = (HasAPIKey,)   

    def get(self, request):
        print(request.GET)

        return Response({}, status=200)


class CustomUserDocumentDownload(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    manual_parameters = [
        'cronograma', 'atestado_de_matricula', 'atestado_de_frequencia',
        'historico_escolar'
    ]

    @swagger_auto_schema(operation_summary='Faz download de um documento relacionado a um aluno', manual_parameters=[
        openapi.Parameter(
            'file',
            openapi.IN_QUERY,
            description='Selected File',
            type=openapi.TYPE_STRING,
            enum=manual_parameters,
            default=manual_parameters[0]
        )
    ])
    def get(self, request, aluno_uuid):
        user = models.CustomUser.objects.get(uuid=aluno_uuid)

        if user.role != user.ALUNO:
            return Response({'error': 'Usuário inválido para essa requisição'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.GET.get('file', self.manual_parameters[0])
        dados_para_pdf = {
            'coordenador': {
                'nome': 'Bruno Figueiredo Coelho',
                'contato': '40028922'
            },
            'instituicao': {
                'nome': 'ivo silveira',
                'endereco': 'rua dos anjos 12'
            },
            'aluno': {
                'nome': f'{user.first_name} {user.last_name}',
                'matricula': user.username,
                'turma': user.turma.nome,
                'turno': models.Turma.TURNO_CHOICES[user.turma.turno - 1][1]
            }
        }

        if file == self.manual_parameters[0]:
            response = Response({'url': request.build_absolute_uri(user.turma.calendario.url), 'title': user.turma.calendario.name, 'content-type': mimetypes.guess_type(user.turma.calendario.name)[0]})
        elif file == self.manual_parameters[1]:
            buffer = pdf_utils.gerar_atestado_de_matricula(dados_para_pdf)
            filename = f'atestado_de_matricula_{str(user.first_name + user.last_name).replace(' ', '_')}.pdf'
            file_name = default_storage.save(filename, buffer)
            response = Response({'url': request.build_absolute_uri(default_storage.url(file_name)), 'title': file_name, 'content-type': mimetypes.guess_type(file_name)[0]}, status=status.HTTP_200_OK)
        elif file == self.manual_parameters[2]:
            buffer = pdf_utils.gerar_atestado_de_frequencia(dados_para_pdf)
            filename = f'atestado_de_frequencia_{str(user.first_name + user.last_name).replace(' ', '_')}.pdf'
            file_name = default_storage.save(filename, buffer)
            response = Response({'url': request.build_absolute_uri(default_storage.url(file_name)), 'title': file_name, 'content-type': mimetypes.guess_type(file_name)[0]}, status=status.HTTP_200_OK)
        elif file == self.manual_parameters[3]:
            disciplinas = models.CustomUserDisciplina.objects.filter(custom_user__uuid=aluno_uuid)
            
            data = [
                ['Disciplina', 'Nota', 'Faltas'],
            ]
            data.extend([[i.disciplina.nome, f'{statistics.mean(i.notas):.2f}', f'{i.falta}'] for i in disciplinas])
            dados_para_pdf['historico'] = data

            buffer = pdf_utils.gerar_historico_escolar(dados_para_pdf)
            filename = f'historico_escolar_{str(user.first_name + user.last_name).replace(' ', '_')}.pdf'
            file_name = default_storage.save(filename, buffer)
            response = Response({'url': request.build_absolute_uri(default_storage.url(file_name)), 'title': file_name, 'content-type': mimetypes.guess_type(file_name)[0]}, status=status.HTTP_200_OK)

        return response


class BotDocumentDownload(views.APIView):
    authentication_classes = ()
    permission_classes = (HasAPIKey, )

    manual_parameters = [
        'relatorio_acoes'
    ]

    @swagger_auto_schema(operation_summary='Faz o download de um documento relacionado ao bot', manual_parameters=[
        openapi.Parameter(
            'file',
            openapi.IN_QUERY,
            description='Selected File',
            type=openapi.TYPE_STRING,
            enum=manual_parameters,
            default=manual_parameters[0]
        )
    ])
    def get(self, request):
        return Response({}, status=200)
