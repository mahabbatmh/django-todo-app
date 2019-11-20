from django.contrib import admin
from .models import Todo, TodoUser, Comment

todosModels = [Todo, TodoUser, Comment]

admin.site.register(todosModels)
