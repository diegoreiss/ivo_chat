from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views


urlpatterns = [
    path('token/', view=TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', view=TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', view=views.CustomUserListCreate.as_view(), name='customuser_view_create'),
    path('user/role/', view=views.CustomUserCurrentRetrieve.as_view(), name='customuser_current_role_view'),
    path('user/<int:pk>/', view=views.CustomUserRetrieveUpdateDestroy.as_view(), name='customuser_view_update'),
]
