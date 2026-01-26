from django.db import models

class Video(models.Model):
    name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
