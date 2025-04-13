from django.conf import settings
from django.db import models

class TestResult(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    raw_answers = models.JSONField()
    dimension_scores = models.JSONField()
    dimension_averages = models.JSONField()
    dimension_counts = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"TestResult {self.user.username} at {self.created_at}"
