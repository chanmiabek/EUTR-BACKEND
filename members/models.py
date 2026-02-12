from django.db import models
from django.conf import settings

class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    skills = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.email

# Create your models here.
