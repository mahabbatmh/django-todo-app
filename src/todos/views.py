import json

import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect
from django.db import transaction, Error
from datetime import timedelta
import logging

from .forms import TodoForm
from .models import TodoUser
from .tasks import send_notification
from django.utils import timezone

logger = logging.getLogger('Django')


def create_view(request):
    form = TodoForm(request.POST or None)

    if form.is_valid():
        try:
            with transaction.atomic():
                local_timezone_str = form.cleaned_data['client_time_zone']
                todo = form.save()
                todo_user = TodoUser(user=request.user, todo=todo, is_owner=True)
                todo_user.save()
                local_timezone = pytz.timezone(local_timezone_str)
                time_delay = local_timezone.localize(todo.complete_date).astimezone(pytz.utc) - timedelta(minutes=10)
                print(time_delay)
                send_notification.apply_async(args=('Todo Notification',
                                                    "{0} must be complete after 10 minutes".format(
                                                        todo.title), [request.user.email],),
                                              eta=time_delay
                                              )
                return redirect('/')
        except Error:
            logger.error(Error)

    context = {
        'form': form
    }

    return render(request, 'todos/create.html', context)


@login_required
def index(request):
    todo_users = TodoUser.objects.select_related().filter(user=request.user)
    context = {
        "todo_users": todo_users
    }
    return render(request, 'todos/list.html', context)


@login_required
def edit_view(request, id):
    try:
        todo_user = TodoUser.objects.select_related().get(todo_id=id, user=request.user, is_owner=True)
    except ObjectDoesNotExist:
        todo_user = None
    if todo_user:
        users = User.objects.all().values()
        todos = TodoUser.objects.filter(todo_id=id).values()
        for i in range(len(users)):
            users[i]["has_access"] = False
            for j in range(len(todos)):
                print(users[i])
                if users[i]["id"] == todos[j]["user_id"]:
                    users[i]["has_access"] = True
                    break
        context = {
            "todo": todo_user.todo,
            "users": users
        }
        return render(request, 'todos/edit.html', context)
    else:
        return redirect('/')


def todo_user_view(request):
    if request.user.is_authenticated and request.POST:
        if request.POST["del"] == "true":
            TodoUser.objects.get_or_create(todo_id=request.POST["todo_id"], user_id=request.POST["user_id"],
                                           is_owner=False)
            res_json = json.dumps({'success': True})
            return HttpResponse(res_json)
        else:
            TodoUser.objects.filter(todo_id=request.POST["todo_id"], user_id=request.POST["user_id"]).delete()
            res_json = json.dumps({'success': True})
            return HttpResponse(res_json)
    else:
        return HttpResponseForbidden()