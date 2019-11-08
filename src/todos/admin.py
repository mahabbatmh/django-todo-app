from django.contrib import admin
from .models import Todo, TodoUser

todosModels = [Todo, TodoUser]

admin.site.register(todosModels)
