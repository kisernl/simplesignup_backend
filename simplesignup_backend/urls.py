# simplesignup_backend/simplesignup_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt # Import csrf_exempt
from simplesignup import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', csrf_exempt(views.RegisterView.as_view()), name='register'),
    path('api/', include('simplesignup.urls')),  # Include your app's URLs under the /api/ prefix
]