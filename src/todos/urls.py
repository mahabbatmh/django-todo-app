from django.urls import path

from .views import index, create_view, edit_view, todo_user_view

urlpatterns = [
    path('', index, name='home'),
    path('create/', create_view, name='todos-create'),
    path('edit/<int:id>', edit_view, name='todos-edit'),
    path('todo-user-rel', todo_user_view, name="todo-user")
]
