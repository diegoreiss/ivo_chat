from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', views.CustomUserListCreate.as_view(), name='customuser-view-create'),
    path('user/<int:pk>', views.CustomUserRetrieveUpdateDestroy.as_view(), name='customuser_view_update')
]
