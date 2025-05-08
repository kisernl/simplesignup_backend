# simplesignup/urls.py
from django.urls import path
from .views import RegisterView, EventListView, RequestLoginLinkView, EmailLoginConfirmView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-login-link/', RequestLoginLinkView.as_view(), name='request_login_link'),
    path('login/confirm/<uuid:token>/', EmailLoginConfirmView.as_view(), name='email_login_confirm'),
    path('events/', EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', EventListView.as_view(), name='event-detail'),  # For PUT (update) and DELETE (delete)
    # Add other URLs specific to your 'simplesignup' app here
]