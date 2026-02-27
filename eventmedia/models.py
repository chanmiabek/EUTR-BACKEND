from django.db import models


class EventOverviewVideo(models.Model):
    title = models.CharField(max_length=160)
    youtube_url = models.URLField()
    image = models.ImageField(upload_to="event-overview/", blank=True, null=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
