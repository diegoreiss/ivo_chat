from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from . import views


urlpatterns = [
    path('token/', view=TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', view=TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('user/', view=views.CustomUserListCreate.as_view(), name='customuser_view_create'),
    path('user/role/aluno/', view=views.CustomUserByRoleAlunoAPIView.as_view(), name='customuser_by_role_admin_view'),
    path('user/current/', view=views.CustomUserCurrentRetrieve.as_view(), name='customuser_current_role_view'),
    path('user/<str:uuid>/role/aluno/update/password', view=views.CustomUserChangePasswordAPIView.as_view(), name='customuser_password_update'),
]
