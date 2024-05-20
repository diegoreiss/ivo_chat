from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from . import views


token_urls = [
    path('token/', view=TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', view=TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]

user_urls = [
    path('user/', view=views.CustomUserListCreate.as_view(), name='customuser_view_create'),
    path('user/role/aluno/', view=views.CustomUserByRoleAlunoAPIView.as_view(), name='customuser_by_role_admin_view'),
    path('user/current/', view=views.CustomUserCurrentRetrieve.as_view(), name='customuser_current_role_view'),
    path('user/<str:uuid>/role/aluno/update/password', view=views.CustomUserChangePasswordAPIView.as_view(), name='customuser_password_update'),
]

bot_urls = [
    path('bot/intent/', view=views.IntentListCreate.as_view(), name='intent_view_create'),
    path('bot/intent/names', view=views.IntentNamesList.as_view(), name='intent_list_names'),
    path('bot/intent/names/available', view=views.AvailableIntentNamesList.as_view(), name='available_intent_list_names'),
    path('bot/intent/<str:intent>', view=views.IntentListBy.as_view(), name='intent_list_by'),
    path('bot/intent/<str:intent>/change/examples', view=views.IntentUpdateExamples.as_view(), name='intent_update_examples'),
    path('bot/response/', view=views.ResponseRetrieveCreate.as_view(), name='response_view_create'),
    path('bot/response/names/', view=views.ResponseNamesRetrieve.as_view(), name='response_list_names'),
    path('bot/response/<str:response_name>/change/texts/', view=views.ResponsesUpdateTexts.as_view(), name='response_update_texts'),
    path('bot/stories/', view=views.StoriesListCreate.as_view(), name='stories_list_create'),
    path('bot/stories/<str:story>/change/steps/', view=views.StoriesStepsUpdate.as_view(), name='stories_update_steps'),
]

urlpatterns = [
    *token_urls,
    *user_urls,
    *bot_urls
]


