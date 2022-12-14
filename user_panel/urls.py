from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'user-panel'

router = routers.DefaultRouter()
# router.register('watch-list', views.WatchListViewSet)
# router.register('watch-list-item', views.WatchListItemViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    # path('', schema_view),
    path('info/', views.UserInfoView.as_view(), name='user-info'),
    path('signup/', views.SignUpAPIView.as_view(), name='user-signup'),
    path('resend/', views.ResendSignUpTokenAPIView.as_view(), name='resend-token'),
    path('verify-user/', views.UserPhoneRegisterAPIView.as_view(), name='verify-user'),
    path('national-code-verify/', views.UserNationalCodeVerifyAPIView.as_view(), name='national-code-verify'),
    path('national-code-register/', views.UserNationalCodeRegisterAPIView.as_view(), name='national-code-register'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('forget-password-token/', views.SendPassForgotTokenAPIView.as_view(), name='forget-password-token'),
    path('forget-password-verify/', views.VerifyPassForgotTokenAPIView.as_view(), name='forget-password-verify'),
]
