from django.db import models
from django.utils import timezone

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    vimeo_id = models.CharField(max_length=50)
    upload_date = models.DateTimeField(default=timezone.now)
    thumbnail_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, default='processing')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-upload_date']
