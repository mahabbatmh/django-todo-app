import json

import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.db import transaction, Error
from datetime import timedelta
import logging

from .forms import TodoForm
from .models import TodoUser, Comment, PermissionEnum
from .tasks import send_notification

logger = logging.getLogger('Django')


def create_view(request):
    form = TodoForm(request.POST or None)

    if form.is_valid():
        try:
            with transaction.atomic():
                local_timezone_str = form.cleaned_data['client_time_zone']
                todo = form.save()
                todo_user = TodoUser(user=request.user, todo=todo, permission=PermissionEnum.EDIT.value)
                todo_user.save()
                local_timezone = pytz.timezone(local_timezone_str)
                time_delay = local_timezone.localize(todo.complete_date).astimezone(pytz.utc) - timedelta(minutes=10)
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
def detail_view(request, id):
    try:
        todo_user = TodoUser.objects.select_related().get(todo_id=id, user=request.user)
        comments = None
        if todo_user.permission in (PermissionEnum.COMMENT.value, PermissionEnum.EDIT.value):
            comments = Comment.objects.select_related().filter(todo_id=id).order_by('created')
    except ObjectDoesNotExist:
        comments = None
        todo_user = None
    try:
        is_owner = TodoUser.objects.select_related().get(todo_id=id, user=request.user,
                                                         permission=PermissionEnum.EDIT.value)
    except ObjectDoesNotExist:
        is_owner = None
    if todo_user:
        users = User.objects.all().values()
        todos = TodoUser.objects.filter(todo_id=id).values()
        for i in range(len(users)):
            users[i]["has_access"] = False
            for j in range(len(todos)):
                if users[i]["id"] == todos[j]["user_id"]:
                    users[i]["has_access"] = True
                    break
        context = {
            "todo": todo_user.todo,
            "is_owner": True if is_owner else False,
            "comments": comments,

        }
        return render(request, 'todos/detail.html', context)
    else:
        return redirect('/')


def todo_user_view(request):
    if request.user.is_authenticated and request.POST:
        form_data = request.POST
        try:
            todo_user_owner = TodoUser.objects.select_related().get(todo_id=form_data['todo_id'],
                                                                    user=request.user,
                                                                    permission=PermissionEnum.EDIT.value)
            assign_user = User.objects.filter(Q(username=form_data['user_identificator']) |
                                              Q(email=form_data['user_identificator'])).get()
            try:
                TodoUser.objects.get(user=assign_user, todo_id=form_data['todo_id']).delete()
            except ObjectDoesNotExist:
                pass
            new_todo_user = TodoUser(user=assign_user, todo_id=form_data['todo_id'], permission=form_data['permission'])
            new_todo_user.save()
            res_json = json.dumps({'success': 'true'})
            return HttpResponse(res_json)
        except ObjectDoesNotExist:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()


@login_required
def remove_comment(request):
    if request.POST:
        try:
            comment = Comment.objects.select_related().get(id=request.POST['comment_id'])
            todo_user = TodoUser.objects.get(todo_id=request.POST['todo_id'], user=request.user)
            if not (comment.user.id == request.user.id or todo_user.is_owner):
                return HttpResponseForbidden()
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        Comment.objects.filter(id=request.POST['comment_id']).delete()
        res_json = json.dumps({'success': 'true'})
        return HttpResponse(res_json)

    return HttpResponseForbidden()
