from django.urls import path

from .views import index, create_view, detail_view, todo_user_view, remove_comment

urlpatterns = [
    path('', index, name='home'),
    path('create/', create_view, name='todos-create'),
    path('detail/<int:id>', detail_view, name='todos-detail'),
    path('todo-user-rel', todo_user_view, name="todo-user"),
    path('remove-comment', remove_comment, name='remove-comment')
]
