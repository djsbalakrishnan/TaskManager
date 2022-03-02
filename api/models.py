from django.db import models

from django.contrib.auth.models import User


class ToDo(models.Model):
    """ ToDo Model """
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
