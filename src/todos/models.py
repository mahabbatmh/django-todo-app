from django.conf import settings
from django.db import models
from enum import Enum

from django.utils import timezone


class PermissionEnum(Enum):
    READ = "100"
    COMMENT = "110"
    EDIT = "111"


class Todo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(default=timezone.now)
    complete_date = models.DateTimeField()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title


class TodoUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    permission = models.CharField(max_length=3,
                                  choices=[(permission, permission.value) for permission in PermissionEnum],
                                  default=PermissionEnum.READ.value)

    def __str__(self):
        return "{0} {1}".format(self.user.email, self.todo.title)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    message = models.TextField(blank=False)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{0}".format(self.user.email, self.todo.title)
