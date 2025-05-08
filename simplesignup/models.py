# simplesignup/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    is_pro = models.BooleanField(default=False)
    registration_date = models.DateTimeField(default=timezone.now)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="simplesignup_user_set",  # Add a unique related_name
        related_query_name="simplesignup_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="simplesignup_user_set",  # Add a unique related_name
        related_query_name="simplesignup_user",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
# simplesignup/models.py
class Event(models.Model):
    creator = models.ForeignKey(User, related_name='created_events', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    attendees = models.ManyToManyField(User, related_name='attended_events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class EmailLoginToken(models.Model):
    user = models.ForeignKey('simplesignup.User', on_delete=models.CASCADE, related_name='login_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Set an expiration time (e.g., 15 minutes from creation)
        self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token for {self.user.email}"