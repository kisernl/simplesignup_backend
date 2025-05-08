# simplesignup/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import EmailLoginToken, Event
from django.contrib.auth import login, get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, EventSerializer

# Get the custom user model
User = get_user_model()


class RequestLoginLinkView(APIView):
    authentication_classes = []
    permission_classes = []  # Allow unauthenticated access
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use the User model obtained from get_user_model()
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Optionally, you might want to avoid revealing if an email exists
            return Response({'message': 'Login link sent if the email exists'}, status=status.HTTP_200_OK)

        # Create a new login token for the user
        token = EmailLoginToken.objects.create(user=user)

        # Generate the login link
        login_url = reverse('email_login_confirm', kwargs={'token': str(token.token)})
        full_login_url = request.build_absolute_uri(login_url)

        # Send the email
        subject = 'Your Login Link'
        message = f'Click the following link to log in: {full_login_url}'
        from_email = settings.DEFAULT_FROM_EMAIL  # Configure in settings.py
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Login link sent to your email'}, status=status.HTTP_200_OK)


class EmailLoginConfirmView(APIView):
    def get(self, request, token):
        try:
            login_token = EmailLoginToken.objects.get(token=token)
        except EmailLoginToken.DoesNotExist:
                return Response({'error': 'Invalid login link'}, status=status.HTTP_400_BAD_REQUEST)

        if login_token.expires_at < timezone.now():
            login_token.delete()
            return Response({'error': 'Login link has expired'}, status=status.HTTP_400_BAD_REQUEST)

        user = login_token.user
        login_token.delete()  # Invalidate the token after use

        # Log the user in (using Django's built-in login for session-based auth)
        # This is for session-based login, which might not be needed if you're purely using JWTs
        # If you are purely using JWTs, you might remove this line.
        login(request, user)

        # Generate and return JWT tokens
        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        }
        # If purely JWT, return the tokens and the frontend handles redirection/state
        return Response(response_data, status=status.HTTP_200_OK)

        # If you need session *and* JWT, keep the login(request, user) and return tokens.
        # If you are redirecting to a frontend after login confirmation:
        # frontend_redirect_url = settings.FRONTEND_LOGIN_SUCCESS_URL
        # return redirect(f'{frontend_redirect_url}?access={response_data["access"]}&refresh={response_data["refresh"]}')


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        # UserSerializer should also use get_user_model() internally or be compatible
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventListView(APIView):
    authentication_classes = [JWTAuthentication] # Add JWT Authentication
    permission_classes = [IsAuthenticatedOrReadOnly] # Require authentication for all methods

    def get(self, request):
        # for GET, using permission_classes = [IsAuthenticatedOrReadOnly]
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        if event.creator != request.user: 
            raise PermissionDenied("You do not have permission to update this event.")

        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_NOT_FOUND)

        if event.creator != request.user: 
            raise PermissionDenied("You do not have permission to delete this event.")

        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)